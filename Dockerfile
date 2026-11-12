# 1. Use an official slim Python base image
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /code

# Install curl for healthchecks and clean up apt cache
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# 3. Leverage layer caching by installing dependencies first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Create a non-root user and ensure write permissions for the data directory
RUN useradd -m appuser && mkdir -p /code/data && chown -R appuser:appuser /code

# 5. Copy the application code with proper ownership
COPY --chown=appuser:appuser . .

# Switch to the non-root user
USER appuser

EXPOSE 8000

# 6. Healthcheck to verify the app is responding
#HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
CMD curl -f http://localhost:8000/ || exit 1

# 7. Start the FastAPI server with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips=*"]

# Flask option:
# CMD ["python", "-m", "flask", "--app", "app.main", "run", "--host=0.0.0.0", "--port=8000"]
