FROM python:3.11-slim

# Install netcat for healthcheck
RUN apt-get update \
    && apt-get install -y --no-install-recommends netcat-openbsd ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home appuser

WORKDIR /home/appuser/app

# Copy only server code
COPY serveur /home/appuser/app/serveur

RUN chown -R appuser:appuser /home/appuser/app
USER appuser

ENV PYTHONUNBUFFERED=1

# We EXPOSE the default port, but Docker users can override
EXPOSE 9000

# Run server with CLI args used by your argparse parser
CMD ["python", "-m", "serveur.main", \
     "--host", "0.0.0.0", \
     "--port", "9000", \
     "--persist", \
     "--persist-path", "/data/tasks.json"]
