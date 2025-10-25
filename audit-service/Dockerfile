# Dockerfile for api-gateway, phi-service, AND audit-service
FROM python:3.9-slim
WORKDIR /app
# Install Python dependencies
RUN pip install fastapi "uvicorn[standard]" httpx pydantic
COPY ./main.py /app/
# Run the web server on port 8080 when container starts
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]