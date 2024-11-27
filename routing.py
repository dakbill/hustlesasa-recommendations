from fastapi import APIRouter
from graph_repository import get_buyer_recommendations, get_product_recommendations

router = APIRouter()


@router.get("/buyers/{buyer_id}/recommendations")
def buyer_recommendations(buyer_id:int):
    return get_buyer_recommendations(buyer_id)


@router.get("/products/{product_id}/recommendations")
def product_recommendations(product_id: int):
    return get_product_recommendations(product_id)
