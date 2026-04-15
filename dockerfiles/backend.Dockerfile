FROM python:3.13-slim AS builder

ARG SRC_DIR

RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq-dev gcc python3-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv

WORKDIR /app

COPY ${SRC_DIR}/pyproject.toml .
COPY ${SRC_DIR}/uv.lock .

RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system .


FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/usr/local/bin:$PATH"
ENV PYTHONPATH=/app

ARG SRC_DIR

RUN apt-get update --fix-missing && apt-get -y install --no-install-recommends \
        libpq-dev netcat-traditional jq curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /usr/local /usr/local
COPY shared/bootstrap/ /app/bootstrap/
COPY ${SRC_DIR}/src /app