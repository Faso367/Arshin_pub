from datetime import datetime, timedelta, timezone
from app.repositories.auth import AuthRepository
import jwt
from app.schemas.auth import TokenData
from .errorHandler import handle_auth_repo_errors
from redis import ConnectionPool

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

class AuthService:

    def __init__(self, redisPool: ConnectionPool):
        self.authRepo = AuthRepository(redisPool)
        self.currentTime = datetime.now().isoformat()


    async def create_token(self, username: str, expire_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)) -> TokenData:

        expire = (datetime.now() + expire_delta).isoformat()
        to_encode = {"exp": expire, "sub": username}
        token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return TokenData(token=token, expire=expire, username=username)
        

    @handle_auth_repo_errors
    async def is_username_in_DB_and_active(self, username: str) -> bool:

        result = await self.authRepo.get_username_info(username)

        if not result:
            return False
        
        username_expiry = result.get('expiresAt')
        is_active = result.get('isActive')

        if not is_active:
            return False

        # Если текущая дата больше срока истечения
        elif self.currentTime > username_expiry:
            # Делаем пароль неактивным
            await self.authRepo.deactivate_username(username)
            return False  # Пароль неактивен или истек

        elif username == result.get('key'):
            return True
        
        else:
            raise Exception('Возникло непредвиденно исключение')
        

    @handle_auth_repo_errors
    async def create_and_add_token(self, username: str) -> str:
        tokenData = await self.create_token(username)
        await self.authRepo.add_jwt_token(tokenData)
        return tokenData.token
    

    @handle_auth_repo_errors
    async def get_jwt_token(self, username: str) -> str:
        # получаем инфу о старом токене 
        tokenInfo = await self.authRepo.get_token_info_by_username(username)

        # Если токена нет, то создаем новый
        if not tokenInfo:
            tokenData = await self.create_token(username)
            await self.authRepo.add_jwt_token(tokenData)
            return tokenData.token
                
        oldToken = tokenInfo.get('token')
        # время смерти токена из базы
        tokenExpiry = tokenInfo.get('expiresAt')

        # Если время действия токена истекло, то заменяем старый на новый
        if self.currentTime > tokenExpiry:
            newTokenData = await self.create_token(username)
            await self.authRepo.update_tokenInfo(newTokenData)
            return newTokenData.token
        
        return oldToken  # Текущий токен еще актуален


    @handle_auth_repo_errors
    async def is_token_in_DB_and_active(self, token: str) -> bool:
        '''Проверяет есть ли токен в БД и активный ли он'''
        result = await self.authRepo.get_token_info(token)

        if not result:
            return False
        
        tokenExpiry = result.get('expiresAt')
        is_active = result.get('isActive')
        if is_active == False or self.currentTime > tokenExpiry:
            return False

        elif token == result.get('token'):
            return True
        
        else:
            raise Exception('Возникло непредвиденно исключение')