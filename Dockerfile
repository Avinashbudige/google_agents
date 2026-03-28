# Use official Python slim image
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (secrets excluded via .dockerignore)
COPY . .

# Expose ports for both services
EXPOSE 8000 8501

# Start script runs FastAPI + Streamlit together
COPY start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]
