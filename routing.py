from fastapi import APIRouter
from graph_repository import Neo4jClient


router = APIRouter()
neo4j_client = Neo4jClient()

@router.get("/buyers/{buyer_id}/recommendations")
def buyer_recommendations(buyer_id:int):
    return neo4j_client.get_buyer_recommendations(buyer_id)


@router.get("/products/{product_id}/recommendations")
def product_recommendations(product_id: int):
    return neo4j_client.get_product_recommendations(product_id)
