import base64
import os
from typing import Dict, List, Any, Optional
import httpx

class Neo4jClient:
    def __init__(self, host: str = None, auth: str = None):
        """
        Initialize Neo4j client with host and authentication details.
        
        :param host: Neo4j database host URL
        :param auth: Authentication string (username:password)
        """
        self.host = host or os.getenv('NEO4J_HOST')
        self.auth = auth or os.getenv('NEO4J_AUTH')
        self.db = 'neo4j'
        # self.db = 'hustlesasa_test' if "PYTEST_CURRENT_TEST" in os.environ else 'hustlesasa'
        
        if not self.host or not self.auth:
            raise ValueError("Neo4j host and authentication must be provided")
        
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Basic " + base64.b64encode(
                self.auth.replace('/', ':').encode('utf-8')
            ).decode("utf-8")
        }
        
        self.client = httpx.Client()

    def __del__(self):
        """Ensure the client is closed when the object is deleted."""
        if hasattr(self, 'client'):
            self.client.close()

    def _execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> Dict:
        # print(query,parameters)
        """
        Execute a Cypher query with optional parameters.
        
        :param query: Cypher query string
        :param parameters: Optional query parameters
        :return: Query response as a dictionary
        """
        try:
            response = self.client.post(
                f"{self.host}/db/{self.db}/tx/commit",
                json={
                    "statements": [
                        {
                            "statement": query,
                            **({"parameters": parameters} if parameters else {})
                        }
                    ]
                },
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise RuntimeError(f"Neo4j query failed: {e}") from e

    def write_document(self, collection: str, data: Dict[str, Any]) -> None:
        """
        Write or update a document in the graph database.
        
        :param collection: Node label/collection
        :param data: Document data (must include 'id')
        """
        properties = ', '.join([f'doc.{key} = ${key}' for key in data.keys()])
        key = "{id: $id}"
        
        query = f"MERGE (doc:{collection} {key}) ON CREATE SET {properties} ON MATCH SET {properties}"
        
        self._execute_query(query, data)

    def write_relationship(
        self, 
        source: str, 
        target: str, 
        relationship: str, 
        data: Dict[str, Any], 
        edge_properties: Optional[str] = None
    ) -> None:
        """
        Create or update a relationship between two nodes.
        
        :param source: Source node label
        :param target: Target node label
        :param relationship: Relationship type
        :param data: Relationship data (must include 'id1' and 'id2')
        :param edge_properties: Optional custom edge property update
        """
        default_edge_update = (
            "ON CREATE SET r.weight = 1 "
            "ON MATCH SET r.weight = toInteger(r.weight) + 1"
        )
        
        query = f"""
            MERGE (node1:{source} {{id: $id1}})
            MERGE (node2:{target} {{id: $id2}})
            MERGE (node1)-[r:{relationship}]->(node2)
            {edge_properties if edge_properties else default_edge_update}
        """
        
        self._execute_query(query, data)

    def drop_database(self) -> None:
        """
        Completely clear the database. Use with extreme caution.
        """
        query = "MATCH (n) DETACH DELETE n"
        self._execute_query(query)

    def get_document(self, collection: str, doc_id: Any) -> Optional[Dict]:
        """
        Retrieve a specific document by ID.
        
        :param collection: Node label
        :param doc_id: Document ID
        :return: Document data or None
        """
        query = f"MATCH (doc:{collection} {{id: {doc_id}}}) RETURN doc"
        response = self._execute_query(query)
        
        return response.get('results', [{}])[0].get('data', [{}])[0] if response.get('results') else None


    def get_buyer_recommendations(self, buyer_id: int) -> List[Dict]:
        """
        Get product recommendations for a specific buyer.
        
        :param buyer_id: ID of the buyer
        :return: List of recommended products
        """
        query = f"MATCH p=(a:User{{id: {buyer_id} }})-[r1:IS_FOLLOWING]->(b:User)-[r2:HAS_BOUGHT]->(c:Product) " \
                "OPTIONAL MATCH (c)<-[r3:HAS_RATED]-() " \
                "RETURN c, COALESCE(AVG(r3.rating), 0) + COALESCE(SUM(r2.weight),0) AS weight " \
                "ORDER BY weight DESC "
        
        response = self._execute_query(query)
        
        
        return [
            {**(document['row'][0]),'weight':document['row'][1] }
            for document in response.get('results', [{}])[0].get('data', [])
        ] if response.get('results') else []

    def get_product_recommendations(self, product_id: int) -> List[Dict]:
        """
        Get product recommendations based on a specific product.
        
        :param product_id: ID of the product
        :return: List of recommended products with relationship details
        """
        query = f"MATCH p=(a:Product{{id:{product_id}}})-[r1:ALSO_BOUGHT{{weight: r1.weight}}]->(b:Product) " \
                "OPTIONAL MATCH (b)<-[r2:HAS_RATED]-() " \
                "RETURN b, r1.weight AS weight, COALESCE(AVG(r2.rating), 0) AS average_rating " \
                "ORDER BY (weight + average_rating) DESC "
        
        response = self._execute_query(query)

        
        return [
            {**document['row'][0], 'weight':document['row'][1]} 
            for document in response.get('results', [{}])[0].get('data', [])
        ] if response.get('results') else []

    