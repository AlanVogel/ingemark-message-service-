FROM python:3.12-slim

WORKDIR /srv

# System dependencies for psycopg2
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# Copy source and install
COPY pyproject.toml .
COPY app/ app/
COPY alembic/ alembic/
COPY alembic.ini .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

RUN pip install --no-cache-dir .

# Non-root user for security
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
