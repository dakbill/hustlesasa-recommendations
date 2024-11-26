from collections import Counter
from statistics import mode
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager


import os

from init import destroy, setup
from utils import get_document

API_KEY = os.getenv('API_KEY')
TYPESENSE_HOST = os.getenv('TYPESENSE_HOST')

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup()
    yield
    destroy()

app = FastAPI(lifespan=lifespan)



@app.get("/buyers/{buyer_id}/recommendations")
def buyer_recommendations(buyer_id:str):
    buyer = get_document('users',buyer_id)
    is_following = buyer.get('is_following')
    is_following_purchases = [ 
        get_document('products',product_id)
        for user_id in is_following
        for purchases in get_document('users',user_id).get('purchases')
        for product_id in purchases
    ]
    

    ratings_dict = {}
    recommendations = []
    for product in is_following_purchases:
        # print(product)
        product['rating'] = round(sum(product['ratings'])/len(product['ratings']) if len(product['ratings']) > 0 else 0)
        ratings_dict[product.get('id')] = (product['rating'],product)
        recommendations.append(product)
        


    ratings_dict = dict(sorted(ratings_dict.items(), key=lambda item: -item[1][0]))
    print(ratings_dict)
    # is_following_purchases = sorted(is_following_purchases, key=lambda x: (-ratings_dict[x], x))
    # is_following_purchases = list(dict.fromkeys(is_following_purchases))
    return [ratings_dict[key][1] for key in ratings_dict.keys()]


@app.get("/products/{product_id}/recommendations")
def product_recommendations(product_id: str):
    product = get_document('products',product_id)
    also_bought = product.get('also_bought')
    
    if len(also_bought):
        freq_dict = Counter(also_bought)
        # ratings_dict = {}

        also_bought = sorted(also_bought, key=lambda x: (-freq_dict[x], x))
        also_bought = list(dict.fromkeys(also_bought))
        
        for i,product_id in enumerate(also_bought):
            also_bought[i] = get_document('products',product_id)
            also_bought[i]['frequency'] = freq_dict.get(product_id)
            also_bought[i]['rating'] = round(sum(also_bought[i]['ratings'])/len(also_bought[i]['ratings']) if len(also_bought[i]['ratings']) > 0 else 0)
            # ratings_dict[product_id] = also_bought[i]['rating']
            del also_bought[i]['also_bought']
            del also_bought[i]['buyers']
            del also_bought[i]['ratings']
        product['also_bought'] = also_bought

    
    del product['buyers']
    del product['ratings']
    return product

