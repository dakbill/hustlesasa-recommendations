from collections import Counter
from statistics import mode
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager


import os

import routing
from setup import destroy, setup


API_KEY = os.getenv('API_KEY')
NEO4J_HOST = os.getenv('NEO4J_HOST')

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup()
    yield
    destroy()

app = FastAPI(lifespan=lifespan)
app.include_router(routing.router)