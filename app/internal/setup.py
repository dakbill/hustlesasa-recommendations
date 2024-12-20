import asyncio
from datetime import datetime
import os
import random
import time
from faker import Faker
import faker_commerce
from fastapi.encoders import jsonable_encoder

from ..internal.core_api_mocks import mock_follow, mock_purchase, mock_rate
from ..repositories.graph_repository import Neo4jClient
from ..models.product import Product
from ..models.user import User

INVENTORY_SIZE=int(os.getenv('INVENTORY_SIZE'))
USER_BASE=int(os.getenv('USER_BASE'))


def setup(neo4j_client):
    if "PYTEST_CURRENT_TEST" in os.environ:
        neo4j_client.drop_database()

    faker = Faker('en_US')
    for i in range(USER_BASE):
        user = User(
            id=i+1,
            name=faker.name(),
        )
        document = jsonable_encoder(user)        
        neo4j_client.write_document('User',document)

    item_faker = Faker('en_US')
    item_faker.add_provider(faker_commerce.Provider)
    for i in range(INVENTORY_SIZE):
        item = Product(
            id=i+1,
            name= item_faker.ecommerce_name().capitalize(),
            description=item_faker.sentence(nb_words=10),
            price=round(random.uniform(10.0, 1000.0), 2)
        )
        document = jsonable_encoder(item)
        neo4j_client.write_document('Product', document)
    
    asyncio.create_task(run_main())

def destroy(neo4j_client):
    pass
    # neo4j_client.drop_database()

# mock user actions periodically
async def run_main():
    while "PYTEST_CURRENT_TEST" not in os.environ:
        random.seed(round(time.time() * 1000))
        if random.randint(1, 100) % 2 == 0:
            asyncio.create_task(mock_purchase())
        elif random.randint(1, 100) % 3 == 0:
            asyncio.create_task(mock_follow())
        else:
            asyncio.create_task(mock_rate())
        await asyncio.sleep(5)

