# In api-gateway/main.py
from fastapi import FastAPI, HTTPException, Request # Import Request to read headers
import httpx
import os

app = FastAPI()
# Get the internal K8s service name from environment variable
PHI_SERVICE_URL = os.getenv("PHI_SERVICE_URL", "http://phi-service")

@app.get("/api/patient/{patient_id}")
async def get_patient(patient_id: str, request: Request): # Add request parameter
    master_trace = [f"1. [API Gateway]: Request received for patient {patient_id}."]

    # Prove Load Balancer presence by reading its header
    client_ip = request.headers.get("x-forwarded-for")
    if client_ip:
        master_trace.append(f"1a. [GKE Ingress]: Routed via Load Balancer (Client IP: {client_ip}).")

    master_trace.append("2. [API Gateway]: Calling PHI Service...")
    try:
        async with httpx.AsyncClient() as client:
            # Call the internal phi-service
            response = await client.get(f"{PHI_SERVICE_URL}/patient/{patient_id}")
            response.raise_for_status() # Error if status code >= 400

            data_from_phi_service = response.json()
            phi_data = data_from_phi_service.get("phi_data")
            sub_trace = data_from_phi_service.get("trace_log", [])

            master_trace.extend(sub_trace) # Combine traces

            # Check if phi-service reported an error in its trace
            if data_from_phi_service.get("error"):
                 raise HTTPException(status_code=500, detail=data_from_phi_service.get("error"))

            master_trace.append("7. [API Gateway]: PHI data received. Returning to user.")
            return {"phi_data": phi_data, "trace": master_trace}

    except Exception as e:
        master_trace.append(f"X. [API Gateway]: ERROR - {e}")
        # Return trace even on error
        return {"phi_data": None, "trace": master_trace}

# Health check endpoint for Kubernetes/Ingress
@app.get("/")
async def health_check():
    return {"status": "API is healthy"}