import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from apscheduler.schedulers.background import BackgroundScheduler

from app import models
from app.database import SessionLocal, engine
from app import endpoints
from app import schedules

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


@app.get("/")
def main():
    return RedirectResponse(url="/docs/")


app.include_router(
    endpoints.status.router,
    prefix='/status',
    tags=['status']
)
app.include_router(
    endpoints.curve.router,
    prefix='/curves',
    tags=['curve']
)
app.include_router(
    endpoints.position.router,
    prefix='/positions',
    tags=['position']
)
app.include_router(
    endpoints.bridge.router,
    prefix='/bridge',
    tags=['bridge']
)
app.include_router(
    endpoints.light.router,
    prefix='/lights',
    tags=['lights']
)
app.include_router(
    endpoints.group.router,
    prefix='/groups',
    tags=['groups']
)

if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    job_run = scheduler.add_job(
        schedules.run, trigger='interval', minutes=1
    )
    job_offsets = scheduler.add_job(
        schedules.reset_offsets, trigger='cron', hour=4
    )
    scheduler.start()

    uvicorn.run(app, host="0.0.0.0", port=8080)
