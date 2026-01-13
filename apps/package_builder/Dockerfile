FROM python:3.11.14-alpine3.23

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire monorepo context to access shared modules
COPY . /app

CMD ["python3", "-m", "apps.package_builder.main"]
