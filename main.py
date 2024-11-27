from statistics import mode
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager

import routing
from setup import destroy, setup


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup()
    yield
    destroy()


app = FastAPI(
    title="Recommendation Service",
    description="Provides product and buyer recommendation services",
    version="1.0.0",
    lifespan=lifespan
)
app.include_router(routing.router)