from fastapi import APIRouter
from app.services.graph_service import neo4j_client


router = APIRouter()

@router.get("/buyers/{buyer_id}/recommendations")
def buyer_recommendations(buyer_id:int):
    return neo4j_client.get_buyer_recommendations(buyer_id)


@router.get("/products/{product_id}/recommendations")
def product_recommendations(product_id: int):
    return neo4j_client.get_product_recommendations(product_id)