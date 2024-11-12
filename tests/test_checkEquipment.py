import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_checkEquipment_valid(cl: AsyncClient, auth_header: dict, correct_equipment: dict):
    response = await cl.post(
        "/checkEquipment",
        params=correct_equipment,
        headers=auth_header
    )
    assert response.status_code == 200
    assert [{'result_docnum': 'И-АБ/30-09-2024/376062476', 'verification_date': '2024-09-30', 'applicability': False}]


@pytest.mark.anyio
async def test_checkEquipment_invalid_all_params(cl: AsyncClient, auth_header: dict, correct_equipment: dict):

    correct_equipment['org_title'] = 'ФБУ'
    response = await cl.post(
        "/checkEquipment",
        params=correct_equipment,
        headers=auth_header
    )
    assert response.status_code == 200
    assert [{'result_docnum': None, 'verification_date': None, 'applicability': None}]


@pytest.mark.anyio
async def test_checkEquipment_empty_string(cl: AsyncClient, auth_header: dict, correct_equipment: dict):
    for field_name in correct_equipment.keys():
        # Создаем глуюокую копию (несвязанное копирование)
        data = dict(correct_equipment) 
        data[field_name] = ''

        response = await cl.post(
            "/checkEquipment",
            params=data,
            headers=auth_header
        )
        assert response.status_code == 422
        if field_name == 'send_date':
            assert [{'messages': [f'{field_name}: Даты указываются в формате yyyy-mm-dd']}]
        else:
            assert [{'messages': [f'{field_name}: Value error, Значение не должно быть пустой строкой']}]