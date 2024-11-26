import os
import httpx

API_KEY = os.getenv('API_KEY')
TYPESENSE_HOST = 'http://localhost:8108'

def write_to_typesense(collection,data):
    with httpx.Client() as client:
        response = client.post(
            f"{TYPESENSE_HOST}/collections/{collection}/documents",
            json=data,
            headers={'x-typesense-api-key':API_KEY}
        )
        # print(response.text)

def get_document(collection,id):
    with httpx.Client() as client:
        response = client.get(
            f"{TYPESENSE_HOST}/collections/{collection}/documents/{id}",
            headers={'x-typesense-api-key':API_KEY}
        )
        return response.json()
    
def update_document(collection,id,document):
    with httpx.Client() as client:
        response = client.patch(
            f"{TYPESENSE_HOST}/collections/{collection}/documents/{id}",
            headers={'x-typesense-api-key':API_KEY},
            json=document
        )
        return response.json()

def summarize(products):
    if len(products) < 3:
        return 'and'.join([f"{product.get('name')}[id:{product.get('id')}]" for product in products])
    else:
        return f"""
            {', '.join([f"{product.get('name')}[id:{product.get('id')}]" for product in products[:-2]])} and {products[-1].get('name')}[id:{products[-1].get('id')}]
        """.strip()
        