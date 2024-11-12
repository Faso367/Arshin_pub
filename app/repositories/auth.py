from . import Redis, ConnectionPool, Path
from app.schemas.auth import TokenData
# Настройки подключения к Redis


class AuthRepository(object):

    # Один экземпляр репозитория - одна сессия с БД
    def __init__(self, redisPool: ConnectionPool) -> None:
        self.redisSession = Redis(connection_pool=redisPool)

    def __del__(self):
        # Закрываем соединение, если это необходимо
        if self.redisSession:
            self.redisSession.close()  # Это освободит соединение в пуле

    async def clear_db(self):
        # Очищаем текущую базу данных (по умолчанию - db=0)
        self.redisSession.flushdb()

    async def add_jwt_token(self, tokenData: TokenData):
        self.redisSession.json().arrappend("jwtTokens", Path.root_path(), {
            'token': tokenData.token,
            'owner': tokenData.username,
            'expiresAt': tokenData.expire,
            'isActive': True
        })

    async def __get_info_by_key(self, tableName, keyName, keyValue):
        userKeysInfo = self.redisSession.json().get(tableName, Path.root_path())
        return next((item for item in userKeysInfo if item.get(keyName) == keyValue), None)

    async def get_username_info(self, username: str):
        return await self.__get_info_by_key('userKeys', 'key', username)

    async def deactivate_username(self, username):
        userKeys = self.redisSession.json().get('userKeys', Path.root_path())

        for i, userInfo in enumerate(userKeys):
            if userInfo['key'] == username:
                self.redisSession.json().set('userKeys', Path(f'[{i}].isActive'), False)
                break

    async def get_token_info_by_username(self, username: str):
        return await self.__get_info_by_key('jwtTokens', 'owner', username)

    async def get_token_info(self, token: str):
        return await self.__get_info_by_key('jwtTokens', 'token', token)

    async def update_tokenInfo(self, tokenData: TokenData):
        username = tokenData.username
        expireTime = tokenData.expire
        token = tokenData.token

        # Получим все объекты из Redis
        jwtTokens = self.redisSession.json().get('jwtTokens', Path.root_path())
        tokenDataDict = {
            'owner': username,
            'token': token,
            'expiresAt': expireTime,
            'isActive': True
        }

        # Итерируем по объектам и ищем совпадение по имени пользователя
        for i, tokenInfo in enumerate(jwtTokens):
            if tokenInfo['owner'] == username:
                # Если 'owner' совпадает, изменим значение 'isActive' и сохраним изменения
                self.redisSession.json().set('jwtTokens', Path(f'[{i}]'), tokenDataDict)
                break