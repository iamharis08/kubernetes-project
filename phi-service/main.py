# In phi-service/main.py
from fastapi import FastAPI, HTTPException, Request # Import Request
import httpx
import os

app = FastAPI()
AUDIT_SERVICE_URL = os.getenv("AUDIT_SERVICE_URL", "http://audit-service/log")

@app.get("/patient/{patient_id}")
async def get_patient_data(patient_id: str, request: Request): # Add request parameter
    trace_log = ["3. [PHI Service]: Request received from API Gateway."]

    # Prove Istio sidecar presence by reading its header
    istio_header = request.headers.get('x-request-id')
    if istio_header:
        trace_log.append(f"3a. [Istio Sidecar]: Inbound request intercepted (Trace ID: ...{istio_header[-12:]}).")

    trace_log.append("4. [PHI Service]: Calling Audit Service...")
    try:
        async with httpx.AsyncClient() as client:
            # Call the internal audit-service
            await client.post(AUDIT_SERVICE_URL,
                              json={"level": "INFO", "message": f"PHI for patient {patient_id} was accessed."})
        trace_log.append("5. [Audit Service]: Log received and stored.")

    except Exception as e:
        trace_log.append(f"5. [Audit Service]: CRITICAL ERROR - {e}")
        # Return error in trace, don't raise exception here
        return {"phi_data": None, "trace_log": trace_log, "error": "Audit logging failed."}

    # If audit success, prepare PHI data
    phi_data = {
        "patient_id": patient_id,
        "name": "Fake Jane Doe",
        "dob": "1985-01-15",
        "note": "Patient data is synthetic. Handle as PHI."
    }
    trace_log.append("6. [PHI Service]: Audit success. Returning PHI data.")
    return {"phi_data": phi_data, "trace_log": trace_log}