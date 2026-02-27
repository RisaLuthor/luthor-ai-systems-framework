FROM python:3.12-slim

WORKDIR /app

# System deps (small + safe)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
  && rm -rf /var/lib/apt/lists/*

# Install project
COPY pyproject.toml README.md /app/
COPY src /app/src
RUN pip install --no-cache-dir -e .

EXPOSE 8000

CMD ["uvicorn", "laf.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
