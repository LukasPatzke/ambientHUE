FROM python:3.8-alpine

COPY ./api/requirements.txt /opt/api/requirements.txt
WORKDIR /opt/api

RUN apk add --no-cache --virtual .build-deps gcc libc-dev make \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps gcc libc-dev make \
    && apk add tzdata

EXPOSE 8080

COPY ./api/app /opt/api/app

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

HEALTHCHECK --interval=5m --timeout=3s \
  CMD curl -f http://localhost:8080/ || exit 1

ENTRYPOINT ["gunicorn", "app.main:app", "-b", "0.0.0.0:8080", "-w", "4", "-k", "uvicorn.workers.UvicornWorker",  "--preload"]