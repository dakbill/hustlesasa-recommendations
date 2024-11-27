import os
import random
from graph_repository import Neo4jClient
from utils import summarize

INVENTORY_SIZE=int(os.getenv('INVENTORY_SIZE'))
USER_BASE=int(os.getenv('USER_BASE'))
neo4j_client = Neo4jClient()

# mock user purchase
async def mock_purchase(user_id=None, product_ids=[]):
    user_id = user_id if user_id else random.randint(1,USER_BASE)
    
    is_system_sale = len(product_ids) == 0

    cart_size = random.randint(1,10) if is_system_sale else len(product_ids)
    for i in range(cart_size):
        product_id = random.randint(1,INVENTORY_SIZE) if is_system_sale else product_ids[i]
        neo4j_client.write_relationship('User','Product','HAS_BOUGHT',{'id1':user_id,'id2':product_id})
        await mock_rate(user_id,product_id)
        if is_system_sale:
            product_ids.append(product_id)
        
            
    print(f"[user_id:{user_id}] just purchased {summarize(product_ids)}\n\n")

    for product_id in product_ids:
        for also_bought_product_id in product_ids:
            if product_id != also_bought_product_id:
                neo4j_client.write_relationship('Product','Product','ALSO_BOUGHT',{'id1':product_id,'id2':also_bought_product_id})


# mock user follow
async def mock_follow(user_id=None,following_id=None):
    user_id = user_id if user_id else random.randint(1,USER_BASE)
    following_id = following_id if following_id else random.randint(1,USER_BASE)
    
    neo4j_client.write_relationship('User','User','IS_FOLLOWING',{'id1':user_id,'id2':following_id})
    print(f"[user_id:{user_id}] just followed [user_id:{following_id}]\n\n")

# mock user rating
async def mock_rate(user_id=None,product_id=None):
    user_id = user_id if user_id else random.randint(1,USER_BASE)
    product_id = product_id if product_id else random.randint(1,INVENTORY_SIZE)
    
    rating = random.randint(1,5)

    neo4j_client.write_relationship('User','Product','HAS_RATED',{'id1':user_id,'id2':product_id},f"r.rating = {rating}")
    print(f"[user_id:{user_id}] just rated [product_id:{product_id}] {rating} stars \n\n")
