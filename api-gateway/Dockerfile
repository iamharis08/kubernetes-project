# In api-gateway/Dockerfile (FIXED FOR CACHING)

FROM python:3.9-slim
WORKDIR /app

# 🛑 CRITICAL FIX: Copy the source code BEFORE installing large dependencies.
# This ensures Docker's cache is invalidated if main.py changes.
COPY ./main.py /app/ 

# Install Python dependencies (Will only run if main.py changes)
RUN pip install fastapi "uvicorn[standard]" httpx pydantic

# Run the web server on port 8080 when container starts
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]