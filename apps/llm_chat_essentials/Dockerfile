FROM python:3.11.14-alpine3.23

WORKDIR /app

# Copy requirements from root to leverage caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire monorepo context
COPY . /app

EXPOSE 8000

# Ensure the root is in PYTHONPATH
ENV PYTHONPATH=/app

CMD ["python3", "-m", "apps.llm_chat_essentials.main"]
