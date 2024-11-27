from fastapi.testclient import TestClient
from ...internal.core_api_mocks import mock_purchase, mock_follow
from ...main import recommendations_app
import pytest


client = TestClient(recommendations_app)

@pytest.mark.anyio
async def test_product_recommendations():
    with TestClient(recommendations_app) as client:
        user_1_id = 1
        cart_1_product_ids = [1,2,3,4]
        await mock_purchase(user_1_id,cart_1_product_ids)

        user_2_id = 2
        cart_2_product_ids = [3,4,5,6,7]
        await mock_purchase(user_2_id,cart_2_product_ids)

        product_id = 4
        response = client.get(f"/products/{product_id}/recommendations")
        assert response.status_code == 200

        a = cart_1_product_ids.copy()
        a.remove(product_id)

        b = cart_2_product_ids.copy()
        b.remove(product_id)

        
        recommendations = set([product['id'] for product in response.json()])
        assert set(a).issubset(recommendations) and set(b).issubset(recommendations)


@pytest.mark.anyio
async def test_buyer_recommendations():
    with TestClient(recommendations_app) as client:
        user_1_id = 1
        user_2_id = 2

        await mock_follow(user_2_id,user_1_id)

        cart_1_product_ids = [1,2,3,4,5]
        await mock_purchase(user_1_id,cart_1_product_ids)

        response = client.get(f"/buyers/{user_2_id}/recommendations")
        assert response.status_code == 200

        recommendations = set([product['id'] for product in response.json()])

        a = cart_1_product_ids.copy()
        assert set(a).issubset(recommendations)
    