import pytest
from httpx import AsyncClient
import json

@pytest.mark.anyio
async def test_checkEquipment_valid(cl: AsyncClient, auth_header: dict):
    response = await cl.post(
        "/vri",
        params={'result_docnum': 'С-ВТ/26-08-2024/377965643', 'rows': 1},
        headers=auth_header
    )
    assert response.status_code == 200
    correct_item = [item for item in json.loads(response.content) if item.get('result_docnum') == 'С-ВТ/26-08-2024/377965643']
    assert correct_item