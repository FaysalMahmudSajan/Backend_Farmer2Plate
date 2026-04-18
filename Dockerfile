FROM python:3.13-slim

# System dependencies install
RUN apt-get update && apt-get install -y libpq-dev gcc

# Workdir set
WORKDIR /app

# Requirements install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Run app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]