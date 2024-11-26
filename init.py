import asyncio
import json
import os
import random
from faker import Faker
import faker_commerce
from fastapi.encoders import jsonable_encoder
import httpx

from models import Product, User
from utils import get_document, summarize, update_document, write_to_typesense

INVENTORY_SIZE=1000
USER_BASE=100
API_KEY = os.getenv('API_KEY')
TYPESENSE_HOST = os.getenv('TYPESENSE_HOST')

def setup():
    
    with open('schemas.json', 'r') as file:
        for schema in json.load(file):
            create_schema(schema)
    faker = Faker('en_US')
    for i in range(USER_BASE):
        user = User(
            id=str(i+1),
            name=faker.name(),
        )
        document = jsonable_encoder(user)
        document =  document | {'is_following':[],'purchases':[]}
        write_to_typesense('users',document)

    item_faker = Faker('en_US')
    item_faker.add_provider(faker_commerce.Provider)
    for i in range(INVENTORY_SIZE):
        item = Product(
            id=str(i+1),
            name= item_faker.ecommerce_name().capitalize(),
            description=item_faker.sentence(nb_words=10),
            price=round(random.uniform(10.0, 1000.0), 2)
        )
        document = jsonable_encoder(item)
        document =  document | {'buyers':[],'ratings':[],'also_bought':[]}
        write_to_typesense('products', document)
    
    asyncio.create_task(run_main())

def destroy():
    with open('schemas.json', 'r') as file:
        with httpx.Client() as client:
            for schema in json.load(file):
                response = client.delete(
                    f"{TYPESENSE_HOST}/collections/{schema.get('name')}",
                    headers={'x-typesense-api-key':API_KEY}
                )
                print(response.text)


def create_schema(schema):
    with httpx.Client() as client:
        response = client.post(
            f"{TYPESENSE_HOST}/collections",
            json=schema,
            headers={'x-typesense-api-key':API_KEY}
        )
        # print(response.text)


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
    user_id = user_id if user_id else str(random.randint(1,USER_BASE))
    user = get_document('users',user_id)
    products = []
    
    is_system_sale = len(product_ids) == 0

    cart_size = random.randint(1,10)+1 if is_system_sale else len(product_ids)
    for i in range(cart_size):
        product_id = str(random.randint(1,INVENTORY_SIZE)) if is_system_sale else product_ids[i]
        product = get_document('products',product_id)
        product.get('buyers').append(user_id)
        products.append(product)
        user.get('purchases').append(product_id)
        if  is_system_sale:
            product_ids.append(product.get('id'))
            await mock_rate(user,product)
        
            
        
        
    update_document('users',user.get('id'),user)
    print(f"{user.get('name')}[id:{user_id}] just purchased {summarize(products)}\n\n")

    for product in products:
        product['also_bought'] = (product['also_bought'] if product['also_bought'] else []) + product_ids
        update_document('products', product.get('id'), product)
    


# mock user follow
async def mock_follow(user_id=None,following_id=None):
    user_id = user_id if user_id else str(random.randint(1,USER_BASE))
    user = get_document('users',user_id)

    following_id = following_id if following_id else str(random.randint(1,USER_BASE))
    following = get_document('users',following_id)

    
    user.get('is_following').append(following_id)
    user['is_following'] = list(set(user.get('is_following')))

    update_document('users',user_id,user)
    print(f"{user.get('name')}[id:{user_id}] just followed {following.get('name')}[id:{following_id}]\n\n")

# mock user rating
async def mock_rate(user=None,product=None):
    user = user if user else get_document('users',str(random.randint(1,USER_BASE)))
    product = product if product else get_document('products',str(random.randint(1,INVENTORY_SIZE)))
    rating = random.randint(1,5)
    product.get('ratings').append(rating)
    update_document('products',product.get('id'),product)
    print(f"{user.get('name')} [id:{user.get('id')}] just rated {product.get('name')}[id:{product.get('id')}] {rating} stars \n\n")
