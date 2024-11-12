# conftest.py
import pytest
from app.main import app
from app.startups.db import init_db
from httpx import ASGITransport, AsyncClient
from datetime import date

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    # Вызываем lifespan функцию, которая отвечает за создание пула соединений к postgres
    async with init_db(app):
        yield

@pytest.fixture(scope="session")
async def cl():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as client:
       yield client

@pytest.fixture(scope='session')
async def auth_header(cl: AsyncClient) -> dict:

    postData = {"username": "123456789", "password": "test_password"} 

    response = await cl.post(
        "/token",
        data=postData
    )
    respJ = response.json()
    if response.status_code == 200:
        if "access_token" in respJ:
            auth_token = respJ['access_token']
            return {"Authorization": f"Bearer {auth_token}"}

    elif response.status_code == 401:
        response = await cl.post(
            "/token",
            json=postData
        )
    return ''

@pytest.fixture(scope='session')
async def correct_equipment() -> dict:
    return {'send_date': date(2024, 9, 30).isoformat(), 'mi_number': 20694, 'mit_number': '728-07', 'org_title': 'ФБУ "ЦСМ ИМ. А.М. МУРАТШИНА В РЕСПУБЛИКЕ БАШКОРТОСТАН"'}