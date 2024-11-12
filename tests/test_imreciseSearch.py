import pytest
from httpx import AsyncClient
import json

@pytest.mark.anyio
async def test_statistics_valid(cl: AsyncClient, auth_header: dict):
    response = await cl.post(
        "/statistics",
        params={'mit_number': '1856-63', 'mit_title': 'Трансформаторы тока измерительные',
                'mit_notation': 'ТВШЛ-10, ТВЛ-10, (ТВЛМ-10 с 1967 г.)', 'mi_modification': 'ТВЛМ-10'},
        headers=auth_header
    )
    assert response.status_code == 200
    assert len(json.loads(response.content)) >= 4