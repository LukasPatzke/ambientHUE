FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-alpine3.10

COPY ./api/requirements.txt /app/requirements.txt
WORKDIR /app/

RUN apk add --no-cache --virtual .build-deps gcc libc-dev make \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps gcc libc-dev make \
    && apk add tzdata curl

COPY ./api /app

ARG BUILD_DATE
ARG VCS_REF
ARG VERSION=dev
LABEL maintainer="LukasPatzke" \
  org.opencontainers.image.created=$BUILD_DATE \
  org.opencontainers.image.url="https://github.com/LukasPatzke/ambientHUE" \
  org.opencontainers.image.source="https://github.com/LukasPatzke/ambientHUE" \
  org.opencontainers.image.version=$VERSION \
  org.opencontainers.image.revision=$VCS_REF \
  org.opencontainers.image.vendor="LukasPatzke" \
  org.opencontainers.image.title="ambientHUE" \
  org.opencontainers.image.licenses="MIT"

HEALTHCHECK --timeout=3s --interval=10s \
  CMD curl -s -f http://localhost:8080/api/status/ || exit 1

ENV PYTHONPATH=/app
ENV GUNICORN_CMD_ARGS="--preload"