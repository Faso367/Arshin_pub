from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
load_dotenv()
import time
import os
from redis import ConnectionPool, Redis
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Boolean, DateTime, select
import asyncpg
from redis.commands.json.path import Path



async def import_UserKeys_to_Redis(redisSession: Redis):
    '''Импорт данных о пользователях из postgres в кэш redis'''
    Base = declarative_base()

    # Определяем модель UserKeys
    class UserKeys(Base):
        __tablename__ = 'UserKeys'
        id = Column(Integer, primary_key=True, autoincrement=True)
        key = Column(String)
        orgName = Column(String)
        expiresAt = Column(DateTime)
        isActive = Column(Boolean, default=True)

    postgres_user = os.getenv("POSTGRES_AUTH_USER")
    postgres_host = os.getenv("POSTGRES_AUTH_HOST")
    postgres_password = os.getenv("POSTGRES_AUTH_PASSWORD")
    postgres_db = os.getenv("POSTGRES_AUTH_DB")
    postgres_port = int(os.getenv("POSTGRES_AUTH_PORT"))

    conString = f'postgresql+asyncpg://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}'
    # Настраиваем соединение с PostgreSQL
    postgresqlAuthEngine = create_async_engine(
        conString,
        echo=True,
        pool_timeout=60,        # Таймаут ожидания соединения
        pool_recycle=10000,       # Время, после которого соединение будет пересоздаваться
        pool_size=2,
        max_overflow=30
    )
    async_session = sessionmaker(
        bind=postgresqlAuthEngine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_session() as session:
        # Извлечение всех значений из таблицы UserKeys
        select_res = await session.execute(select(UserKeys))
        rows = select_res.scalars().all()
        if not rows:
            return {}

        # Преобразование объектов в JSON-совместимый формат
        jsonRes = [{
            'key': row.key,
            'orgName': row.orgName,
            'expiresAt': row.expiresAt.isoformat(),
            'isActive': row.isActive
        } for row in rows]
        # Сохраняем JSON данные в Redis
        redisSession.json().set('userKeys', Path.root_path(), jsonRes)

postgresSession = None
redisPool = None
# Создаем контекст lifespan для управления ресурсами
@asynccontextmanager
async def init_db(app: FastAPI):
    global postgresSession
    global redisPool
    postgres_user = os.getenv("POSTGRES_USER")
    postgres_host = os.getenv("POSTGRES_HOST")
    postgres_password = os.getenv("POSTGRES_PASSWORD")
    postgres_db = os.getenv("POSTGRES_DB")
    postgres_port = int(os.getenv("POSTGRES_PORT"))
    redis_host = os.getenv("REDIS_HOST")
    redis_port = int(os.getenv("REDIS_PORT"))
    conString = f'postgresql+asyncpg://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}'
    engine = create_async_engine(
        conString,
        pool_size=10,
        max_overflow=5,
        pool_timeout=30,
        pool_recycle=1800,
        echo=True
    )
    postgresSession = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    redisPool = ConnectionPool(
        host=redis_host,
        port=redis_port,
        db=0,
        max_connections=30,
        decode_responses=True
    )
    redisSession = Redis(connection_pool=redisPool)
    redisSession.flushdb()
    await import_UserKeys_to_Redis(redisSession)
    redisSession.json().set("jwtTokens", Path.root_path(), [])
    redisSession.close()

    # Указываем, что приложение продолжает выполнение в этом контексте
    yield
    
    # Действия при завершении работы приложения
    await engine.dispose()
    # Убиваем все подключения, в том числе те, которые используются
    redisPool.disconnect(inuse_connections=True)

# Зависимость для создания сессии
async def get_postgres_session():
    #return postgresSession()
    async with postgresSession() as session:
        yield session

async def get_redis_pool():
    return redisPool