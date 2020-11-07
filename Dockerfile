FROM python:3.8-alpine3.10

COPY ./api/requirements.txt /app/requirements.txt
WORKDIR /app/

RUN apk add --no-cache --virtual .build-deps gcc libc-dev make \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps gcc libc-dev make \
    && apk add tzdata curl

COPY ./start.sh /start.sh
RUN chmod +x /start.sh

COPY ./gunicorn_conf.py /gunicorn_conf.py
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
  CMD curl -s -f http://localhost/api/status/ || exit 1

EXPOSE 80

ENV PYTHONPATH=/app

# Run the start script, it will check for an /app/prestart.sh script (e.g. for migrations)
# And then will start Gunicorn with Uvicorn
CMD ["/start.sh"]