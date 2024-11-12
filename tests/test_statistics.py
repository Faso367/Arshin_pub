import pytest
from httpx import AsyncClient
import json

@pytest.mark.anyio
async def test_imreciseSearch_valid(cl: AsyncClient, auth_header: dict):
    response = await cl.post(
        "/imreciseSearch",
        params={'paramName': 'mit_number', 'value': '56147-14'},
        headers=auth_header
    )
    assert response.status_code == 200
    el = '56147-14' in json.load(response).get('paramValues')
    assert el == True