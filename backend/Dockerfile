FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
# Add this to your Dockerfile before installing python requirements
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
