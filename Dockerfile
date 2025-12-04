# ---------------------------
# Stage 1: Builder
# ---------------------------
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# Copy dependency file
COPY requirements.txt .

# Install build dependencies (for wheels, etc.)
RUN apt-get update && \
    apt-get install -y build-essential && \
    pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt && \
    rm -rf /root/.cache/pip

# ---------------------------
# Stage 2: Runtime
# ---------------------------
FROM python:3.11-slim AS runtime

# Set timezone environment variable
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Set working directory
WORKDIR /app

# Install system dependencies (cron, timezone tools)
RUN apt-get update && \
    apt-get install -y cron tzdata && \
    rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY ./app ./app
COPY ./scripts ./scripts

# Copy cron configuration
COPY ./cron/2fa-cron /etc/cron.d/2fa-cron

# Set permissions on cron file
RUN chmod 644 /etc/cron.d/2fa-cron && \
    crontab /etc/cron.d/2fa-cron

# Create volume mount points
RUN mkdir -p /data /app/cron && chmod 755 /data /app/cron

# Expose port 8080
EXPOSE 8080

# Start cron daemon and FastAPI server
CMD service cron start && uvicorn app.main:app --host 0.0.0.0 --port 8080
