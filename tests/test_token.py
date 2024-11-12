# test_auth.py
import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_login_token_valid(cl: AsyncClient):
    response = await cl.post(
        "/token",
        data={"username": "123456789", "password": "test_password"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.anyio
async def test_login_token_no_data(cl: AsyncClient):
    response = await cl.post(
        "/token",
        data={},
    )
    assert response.status_code == 422
    assert response.json() == {'messages': ['username: Field required']}

@pytest.mark.anyio
async def test_login_token_empty_password(cl: AsyncClient):
    response = await cl.post(
        "/token",
        data={"username": "123456789", "password": ""},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.anyio
async def test_login_token_invalid(cl: AsyncClient):
    response = await cl.post(
        "/token",
        data={"username": "12345", "password": "test_password"},
    )
    assert response.status_code == 401
    response = response.json()
    assert response['message'] == 'Некорректное имя или пароль' and response['headers'] == {'WWW-Authenticate': 'Bearer'}