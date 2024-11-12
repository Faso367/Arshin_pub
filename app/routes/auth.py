from app.services.authorization import AuthService
from app.schemas.auth import Token
from app.schemas.error import AuthException
from jwt.exceptions import InvalidTokenError, PyJWTError
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from . import Annotated, APIRouter, Form, Depends, jwt
from redis import ConnectionPool
from app.startups.db import get_redis_pool

router = APIRouter()
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 # Срок жизни access_token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Переопределяем форму, чтобы пароль мог быть пустым
class OAuth2PasswordRequestFormEmptyPassword:
    def __init__(
        self, 
        username: str = Form(),  # Имя пользователя обязательно
        password: str | None = Form(None),  # Пароль может быть пустым
        scope: str = Form(""),
        client_id: str | None = Form(None),
        client_secret: str | None = Form(None),
    ):
        self.username = username
        self.password = password or ""  # Используем пустую строку, если пароль не передан
        self.scopes = scope.split()
        self.client_id = client_id
        self.client_secret = client_secret

# Маршрут доступен только через POST
@router.post('/token')
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestFormEmptyPassword, Depends()],
    redisPool: ConnectionPool = Depends(get_redis_pool)
) -> Token:
    service = AuthService(redisPool)
    if await service.is_username_in_DB_and_active(form_data.username) == False:
        raise AuthException(message="Некорректное имя или пароль")

    token = await service.get_jwt_token(username=form_data.username)
    return Token(access_token=token)


# Функция для подтверждения валидности токена
async def verify_token(token: str = Depends(oauth2_scheme), 
        redisPool: ConnectionPool = Depends(get_redis_pool)
        ) -> str:
    service = AuthService(redisPool)
    credentials_exception = AuthException(message="Не удалось найти пользователя с таким именем")
    
    if token is None or await service.is_token_in_DB_and_active(token) == False:
        raise credentials_exception
    try:
        # Декодируем токен и получаем полезную нагрузку (payload)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        sub: str = payload.get("sub")
        
        if sub is None:
            raise credentials_exception
        
        # Возвращаем объект TokenData с полем username
        return sub

    except PyJWTError:
        raise credentials_exception