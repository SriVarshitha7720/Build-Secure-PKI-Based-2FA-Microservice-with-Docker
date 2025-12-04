# --- STAGE 1: Builder ---
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- STAGE 2: Runtime ---
FROM python:3.11-slim
ENV TZ=UTC

# Install system dependencies (cron, timezone data, and necessary build libs in this stage)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        cron \
        tzdata \
        libssl-dev \
        libffi-dev \
        build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code and keys (CORRECTED SECTION)
COPY app.py .
COPY student_private.pem .
# FIX: Added missing local Python modules needed for imports in app.py
COPY totp_utils.py .
COPY decrypt_and_store.py .
# Added public key files needed for general app function and final proof generation
COPY instructor_public.pem .
COPY student_public.pem .

# Copy scripts folder
COPY scripts /app/scripts

# Copy cron job file
COPY cron/2fa-cron /etc/cron.d/crontab-2fa

# Set up cron (FIX: Append newline before crontab to avoid EOF error)
RUN echo "" >> /etc/cron.d/crontab-2fa && \
    chmod 0644 /etc/cron.d/crontab-2fa && \
    crontab /etc/cron.d/crontab-2fa

# Create volume mount points
RUN mkdir -p /data /cron && chmod 755 /data /cron

# Expose port
EXPOSE 8080

# Start cron and FastAPI server (FIX: Use '&' to background cron and 'exec' for the API)
CMD ["sh", "-c", "cron -f & exec uvicorn app:app --host 0.0.0.0 --port 8080"]