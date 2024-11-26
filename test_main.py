from fastapi.testclient import TestClient
import pytest

from init import mock_follow, mock_purchase

from main import app

client = TestClient(app)

@pytest.mark.anyio
async def test_product_recommendations():
    with TestClient(app) as client:
        user_1_id = '1'
        cart_1_product_ids = ['1','2','3','4']
        await mock_purchase(user_1_id,cart_1_product_ids)

        user_2_id = '2'
        cart_2_product_ids = ['3','4','5','6','7']
        await mock_purchase(user_2_id,cart_2_product_ids)

        product_id = '4'
        response = client.get(f"/products/{product_id}/recommendations")
        assert response.status_code == 200

        recommendations = set([product['id'] for product in response.json().get('also_bought')])
        assert set(cart_1_product_ids).issubset(recommendations) and set(cart_2_product_ids).issubset(recommendations)


@pytest.mark.anyio
async def test_buyer_recommendations():
    with TestClient(app) as client:
        user_1_id = '1'
        user_2_id = '2'

        await mock_follow(user_2_id,user_1_id)

        user_1_id
        cart_1_product_ids = ['1','2','3','4','5']
        await mock_purchase(user_1_id,cart_1_product_ids)

        response = client.get(f"/buyers/{user_2_id}/recommendations")
        assert response.status_code == 200

        json_response = response.json()
        print(json_response)
        recommendations = set([product['id'] for product in json_response])

        assert set(cart_1_product_ids).issubset(recommendations)
    