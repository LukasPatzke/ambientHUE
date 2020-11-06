#!/bin/bash

# Database migrations
alembic upgrade head

exec gunicorn app.main:app \
    --bind 0.0.0.0:8080 \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --preload \
    --log-file=- \
    --access-logfile=- \
    "$@"
