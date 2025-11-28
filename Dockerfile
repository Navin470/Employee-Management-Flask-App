# Dockerfile
# Use official lightweight Python image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire Flask app code
COPY . .

# Create a non-root user (security best practice)
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Expose port 5500 (Flask default)
EXPOSE 5500

# Environment variables (good for production)
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Run the Flask app with Gunicorn (production) or flask run (development)
# Option 1: Production (recommended)
CMD ["gunicorn", "--bind", "0.0.0.0:5500", "app:app"]