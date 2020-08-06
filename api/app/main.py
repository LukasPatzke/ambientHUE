import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from apscheduler.schedulers.background import BackgroundScheduler

from app import models
from app.database import SessionLocal, engine
from app import endpoints
from app import schedules
from app.init_database import init

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


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
    endpoints.header.router,
    prefix='/headers',
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
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="debug")
