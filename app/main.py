from statistics import mode
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager

from .internal.setup import destroy, setup
from .routers import recommendations
from .services import graph_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup(graph_service.neo4j_client)
    yield
    destroy(graph_service.neo4j_client)


recommendations_app = FastAPI(
    title="Recommendation Service",
    description="Provides product and buyer recommendation services",
    version="1.0.0",
    lifespan=lifespan
)
recommendations_app.include_router(recommendations.router)