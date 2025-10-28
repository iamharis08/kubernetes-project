# In audit-service/main.py
from fastapi import FastAPI
from pydantic import BaseModel
import logging

# Configure logging ONCE
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

class LogEntry(BaseModel):
    level: str
    message: str

# Health check endpoint for Kubernetes
@app.get("/")
async def health_check():
    return {"status": "Audit Service is healthy"}

@app.post("/log")
async def log_message(entry: LogEntry):
    # This is the "job" of the audit service.
    # In a real app, this would write to a secure database.
    # For our demo, we just log it to the pod's stdout.
    logging.info(f"AUDIT LOG STORED: [{entry.level}] {entry.message}")

    # --- TRACE LOG UPDATED ---
    # This is its piece of the trace
    trace_log = [
        # Log 10: Istio Sidecar (Inbound) - SIMULATED
        "[Istio Sidecar (Audit Service)]: Inbound request intercepted, decrypting mTLS.",
        # Log 11: Audit Service (App)
        "[Audit Service]: Log received and stored."
    ]
    # --- END OF UPDATES ---

    # Return a success message and its trace segment
    return {
        "status": "logged",
        "trace_log": trace_log
    }
