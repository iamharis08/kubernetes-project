# In audit-service/main.py
from fastapi import FastAPI
from pydantic import BaseModel

# Define the structure of the log message we expect
class LogMessage(BaseModel):
    level: str
    message: str

app = FastAPI()

@app.post("/log")
async def log_message(log: LogMessage):
    # Print to the pod's logs (we'll view this with kubectl logs)
    print(f"[AUDIT LOG] - {log.level}: {log.message}")
    return {"status": "logged"}