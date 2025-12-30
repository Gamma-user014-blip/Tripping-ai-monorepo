FROM python:3.11.14-alpine3.23

WORKDIR ./app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 👇 COPY ONLY THIS SERVICE
COPY . /app

CMD ["python3", "-m", "apps.data_collectors.hotel_retriever.main"]
