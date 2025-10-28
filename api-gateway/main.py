# In api-gateway/main.py
from fastapi import FastAPI, HTTPException, Request 
from fastapi.responses import JSONResponse
import logging # Correctly imported
import httpx
import os

# Configure logging ONCE, outside the functions
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()
PHI_SERVICE_URL = os.getenv("PHI_SERVICE_URL", "http://phi-service")

# Health check endpoint for Kubernetes/Ingress
@app.get("/")
async def health_check():
    return {"status": "API is healthy"}

@app.get("/api/patient/{patient_id}")
async def get_patient(patient_id: str, request: Request):
    # --- TRACE LOG UPDATED ---
    # We will build the trace log exactly as requested.
    master_trace = []

    # Log 1: GKE Ingress
    client_ip = request.headers.get("x-forwarded-for")
    if client_ip:
        master_trace.append(f"[GKE Ingress]: Routes traffic to api-gateway-service (Client IP: {client_ip}).")
    else:
        master_trace.append("[GKE Ingress]: Routes traffic to api-gateway-service (IP not found, check LB config).")

    # Log 2: Istio Sidecar (Inbound) - SIMULATED
    master_trace.append("[Istio Sidecar (API Gateway)]: Inbound request intercepted from Ingress/Load Balancer.")

    # Log 3: API Gateway (App)
    master_trace.append(f"[API Gateway]: Request received for patient {patient_id}.")
    
    # Log 4: API Gateway (App)
    master_trace.append("[API Gateway]: Calling PHI Service...")

    # Log 5: Istio Sidecar (Outbound) - SIMULATED
    master_trace.append("[Istio Sidecar (API Gateway)]: Outbound request intercepted, applying mTLS, and forwarding to phi-service.")
    # --- END OF UPDATES ---
    
    try:
        async with httpx.AsyncClient() as client:
            # Call the internal phi-service
            response = await client.get(f"{PHI_SERVICE_URL}/patient/{patient_id}")
            response.raise_for_status()

            data_from_phi_service = response.json()
            phi_data = data_from_phi_service.get("phi_data")
            sub_trace = data_from_phi_service.get("trace_log", [])

            # This will now contain all the downstream logs (6-11)
            master_trace.extend(sub_trace) 

            # Check if phi-service reported an error in its trace
            if data_from_phi_service.get("error"):
                 raise HTTPException(status_code=500, detail=data_from_phi_service.get("error"))

            # Add our final closing log
            master_trace.append("[API Gateway]: PHI data received. Returning to user.")
            
            return {"phi_data": phi_data, "trace": master_trace}

    # CRITICAL FIX: Ensure the entire exception block is correctly indented.
    except Exception as e:
        # ===> START INDENTED BLOCK <===
        # This logs the message AND the full exception traceback to pod logs
        logging.exception("An error occurred during the request to PHI service.") 
        
        # Prepare data for the frontend response
        # --- TRACE LOG UPDATED ---
        master_trace.append(f"X. [API Gateway]: ERROR - {type(e).__name__}. Check pod logs for full traceback.") 
        # --- END OF UPDATE ---
        
        # Return the error trace to the frontend with a 500 status
        return JSONResponse(
            status_code=500, # Indicate a server error
            content={"phi_data": None, "trace": master_trace}
        )
        # ===> END INDENTED BLOCK <===

@app.get("/api/check")
async def get_check():
    UNAUTHORIZED_URL = "http://audit-service/log" 
    
    trace_log = [
        "1. [API Gateway]: Initiating UNAUTHORIZED call.",
        "2. [API Gateway]: Attempting POST to audit-service (Should be BLOCKED by NetworkPolicy/Istio)..." # Updated message slightly
    ]
    
    try:
        # Keep a reasonable timeout
        async with httpx.AsyncClient(timeout=5.0) as client: # Increased timeout slightly just in case
            response = await client.post(UNAUTHORIZED_URL, json={"level":"DENIAL_TEST", "message":"Test"}) 
            
            # If it gets here, the policy/mesh failed.
            trace_log.append(f"X. [ERROR]: Policy FAILED! Received status {response.status_code}. Egress was NOT blocked.")
            
    # --- THE FIX ---
    # Catch BOTH ConnectTimeout and ReadTimeout as a successful block
    except (httpx.ConnectTimeout, httpx.ReadTimeout) as timeout_err:
        trace_log.append(f"✅ [NetworkPolicy/Istio]: Request timed out ({type(timeout_err).__name__}) - Egress BLOCKED as expected.")
    # ---------------
    
    except Exception as e:
        # Catch other unexpected errors
        trace_log.append(f"X. [Unexpected Error]: {type(e).__name__} - {e}")

    # Return trace 
    return JSONResponse(
        status_code=200, 
        content={"trace": trace_log, "status": "Security Check Complete"}
    )
