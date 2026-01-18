FROM python:3.11.14-alpine3.23

WORKDIR /app

# Copy specific requirements file
COPY apps/data_collectors/flight_retriever/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire mono-repo to access shared modules
COPY . /app

# Run the service
CMD ["uvicorn", "apps.data_collectors.flight_retriever.main:app", "--host", "0.0.0.0", "--port", "8000"]
