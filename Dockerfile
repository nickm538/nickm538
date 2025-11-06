FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY mamdani_tracker/ ./mamdani_tracker/
COPY templates/ ./templates/
COPY static/ ./static/
COPY run.py .

# Set environment variables
ENV FLASK_APP=mamdani_tracker.app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "run.py"]
