from fastapi import APIRouter
from utils import get_document, get_documents

router = APIRouter()


@router.get("/buyers/{buyer_id}/recommendations")
def buyer_recommendations(buyer_id:int):
    query = f"MATCH p=(a:User)-[r1:IS_FOLLOWING]->(b:User)-[r2:HAS_BOUGHT]->(c:Product) where a.id={buyer_id} DESC RETURN c"
    response = get_documents(query)
    documents = []

    if len(response['results'])>0 and len(response['results'][0]['data'])>0:
        documents = [document['row'][0] for document in response['results'][0]['data']]
    return documents


@router.get("/products/{product_id}/recommendations")
def product_recommendations(product_id: int):
    query = f"MATCH p=(a:Product)-[r:ALSO_BOUGHT]->(b:Product) where a.id={product_id} ORDER BY r.weight DESC RETURN b,r"
    response = get_documents(query)
    documents = []

    if len(response['results'])>0 and len(response['results'][0]['data'])>0:
        documents = [document['row'][0]|document['row'][1] for document in response['results'][0]['data']]
    return documents
