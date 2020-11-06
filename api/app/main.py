import logging
import uvicorn
from fastapi import FastAPI
from fastapi.logger import logger as fastapi_logger
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from apscheduler.schedulers.background import BackgroundScheduler

from app import endpoints, schedules
from app.init_database import init

app = FastAPI()

gunicorn_error_logger = logging.getLogger("gunicorn.error")
gunicorn_logger = logging.getLogger("gunicorn")
uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_access_logger.handlers = gunicorn_error_logger.handlers

fastapi_logger.handlers = gunicorn_error_logger.handlers

if __name__ != "__main__":
    fastapi_logger.setLevel(gunicorn_logger.level)
else:
    fastapi_logger.setLevel(logging.DEBUG)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


api = FastAPI(
    title='Ambient Hue',
    description='Make your smart lights smart',
    version='0.0.1',
    root_path='/api'
)

api.include_router(
    endpoints.status.router,
    prefix='/status',
    tags=['status']
)
api.include_router(
    endpoints.curve.router,
    prefix='/curves',
    tags=['curve']
)
api.include_router(
    endpoints.position.router,
    prefix='/positions',
    tags=['position']
)
api.include_router(
    endpoints.bridge.router,
    prefix='/bridge',
    tags=['bridge']
)
api.include_router(
    endpoints.light.router,
    prefix='/lights',
    tags=['lights']
)
api.include_router(
    endpoints.group.router,
    prefix='/groups',
    tags=['groups']
)
api.include_router(
    endpoints.webhook.router,
    prefix='/webhooks',
    tags=['webhooks']
)
api.include_router(
    endpoints.settings.router,
    prefix='/settings',
    tags=['settings']
)

app.mount('/api', api)
app.mount('/app', StaticFiles(directory='build', html=True), name='app')
app.mount('/', RedirectResponse(url='/app/'))

init()

scheduler = BackgroundScheduler()
job_run = scheduler.add_job(
    schedules.run, trigger='interval', minutes=1
)
job_offsets = scheduler.add_job(
    schedules.reset_offsets, trigger='cron', hour=4
)
scheduler.start()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8080,
        log_level="debug",
        reload=True
    )
