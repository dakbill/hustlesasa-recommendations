import base64
import os
import httpx

API_KEY = os.getenv('API_KEY')
NEO4J_HOST = os.getenv('NEO4J_HOST')
NEO4J_AUTH = os.getenv('NEO4J_AUTH')

headers = {
    "Content-Type": "application/json",
    "Authorization": "Basic " + base64.b64encode(NEO4J_AUTH.replace('/',':').encode('utf-8')).decode("utf-8")
}


def get_buyer_recommendations(buyer_id:int):
    query = f"MATCH p=(a:User)-[r1:IS_FOLLOWING]->(b:User)-[r2:HAS_BOUGHT]->(c:Product) where a.id={buyer_id} ORDER BY r2.weight DESC RETURN c"
    response = get_documents(query)
    documents = []

    if len(response['results'])>0 and len(response['results'][0]['data'])>0:
        documents = [document['row'][0] for document in response['results'][0]['data']]
    return documents

def get_product_recommendations(product_id: int):
    query = f"MATCH p=(a:Product)-[r:ALSO_BOUGHT]->(b:Product) where a.id={product_id} ORDER BY r.weight DESC RETURN b,r"
    response = get_documents(query)
    documents = []

    if len(response['results'])>0 and len(response['results'][0]['data'])>0:
        documents = [document['row'][0]|document['row'][1] for document in response['results'][0]['data']]
    return documents

def write_document_to_graph(collection,data):
    properties = ', '.join([ f'doc.{key}= ${key}' for key in data.keys()])
    key = "{id: $id}"
    with httpx.Client() as client:
        response = client.post(
            f"{NEO4J_HOST}/db/neo4j/tx/commit",
            json={
                "statements": [
                    {
                        "statement": f"MERGE (doc:{collection} {key}) ON CREATE SET {properties} ON MATCH SET {properties}",
                        "parameters": data
                    }
                ]
            },
            headers=headers
        )
        # print(response.text)

def write_relationship_to_graph(source,target,relationship,data,edge_properties=None):
    with httpx.Client() as client:
        response = client.post(
            f"{NEO4J_HOST}/db/neo4j/tx/commit",
            json={
                "statements": [
                    {
                        "statement": f"""
                            MERGE (node1:{source} {"{id: $id1}"})
                            MERGE (node2:{target} {"{id: $id2}"})
                            MERGE (node1)-[r:{relationship}]->(node2)
                            ON CREATE SET {edge_properties if edge_properties else 'r.weight = 1'}
                            ON MATCH SET {edge_properties if edge_properties else 'r.weight = toInteger(r.weight) + 1'}
                        """,
                        "parameters": data
                    }
                ]
            },
            headers=headers
        )
        # print(response.text)

def get_document(collection,id):
    with httpx.Client() as client:
        response = client.get(
            f"{NEO4J_HOST}/db/neo4j/tx/commit",
            headers=headers,
        )
        return response.json()

def get_documents(query):
    with httpx.Client() as client:
        response = client.post(
            f"{NEO4J_HOST}/db/neo4j/tx/commit",
            json={
                "statements": [
                    {
                        "statement": query,
                    }
                ]
            },
            headers=headers
        )
        return response.json()


def drop_db():
    return
    with httpx.Client() as client:
        response = client.post(
            f"{NEO4J_HOST}/db/neo4j/tx/commit",
            json={
                "statements": [
                    {
                        "statement": f"MATCH (n) DETACH DELETE n",
                    }
                ]
            },
            headers=headers
        )
        print(response.text)