import asyncio
import os
import random
from faker import Faker
import faker_commerce
from fastapi.encoders import jsonable_encoder

from models import Product, User
from graph_repository import drop_db, write_document_to_graph, write_relationship_to_graph
from utils import summarize

INVENTORY_SIZE=1000
USER_BASE=100
API_KEY = os.getenv('API_KEY')
NEO4J_HOST = os.getenv('NEO4J_HOST')

def setup():
    
    faker = Faker('en_US')
    for i in range(USER_BASE):
        user = User(
            id=i+1,
            name=faker.name(),
        )
        document = jsonable_encoder(user)        
        write_document_to_graph('User',document)

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
        write_document_to_graph('Product', document)
    
    asyncio.create_task(run_main())

def destroy():
    drop_db()




# mock user actions periodically
async def run_main():
    while "PYTEST_CURRENT_TEST" not in os.environ:
        if random.randint(1, 100) % 2 == 0:
            asyncio.create_task(mock_purchase())
        elif random.randint(1, 100) % 3 == 0:
            asyncio.create_task(mock_follow())
        else:
            asyncio.create_task(mock_rate())
        await asyncio.sleep(3)

# mock user purchase
async def mock_purchase(user_id=None, product_ids=[]):
    user_id = user_id if user_id else random.randint(1,USER_BASE)
    
    is_system_sale = len(product_ids) == 0

    cart_size = random.randint(1,10) if is_system_sale else len(product_ids)
    for i in range(cart_size):
        product_id = random.randint(1,INVENTORY_SIZE) if is_system_sale else product_ids[i]
        write_relationship_to_graph('User','Product','HAS_BOUGHT',{'id1':user_id,'id2':product_id})
        await mock_rate(user_id,product_id)
        if is_system_sale:
            product_ids.append(product_id)
        
            
    print(f"[user_id:{user_id}] just purchased {summarize(product_ids)}\n\n")

    for product_id in product_ids:
        for also_bought_product_id in product_ids:
            if product_id != also_bought_product_id:
                write_relationship_to_graph('Product','Product','ALSO_BOUGHT',{'id1':product_id,'id2':also_bought_product_id})


# mock user follow
async def mock_follow(user_id=None,following_id=None):
    user_id = user_id if user_id else random.randint(1,USER_BASE)
    following_id = following_id if following_id else random.randint(1,USER_BASE)
    
    write_relationship_to_graph('User','User','IS_FOLLOWING',{'id1':user_id,'id2':following_id})
    print(f"[user_id:{user_id}] just followed [user_id:{following_id}]\n\n")

# mock user rating
async def mock_rate(user_id=None,product_id=None):
    user_id = user_id if user_id else random.randint(1,USER_BASE)
    product_id = product_id if product_id else random.randint(1,INVENTORY_SIZE)
    
    rating = random.randint(1,5)

    write_relationship_to_graph('User','Product','HAS_RATED',{'id1':user_id,'id2':product_id},f"r.rating = {rating}")
    print(f"[user_id:{user_id}] just rated [product_id:{product_id}] {rating} stars \n\n")
