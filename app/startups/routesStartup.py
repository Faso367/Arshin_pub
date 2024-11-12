from fastapi import FastAPI, Depends, APIRouter
from app.schemas.error import AnyErrorResponse, CustomValidationErrorResponse, AuthException, AuthExceptionResponse
from app.routes import auth, limsClient, arshin, statistics

def init_routes(app: FastAPI) -> FastAPI:

    router = APIRouter()

    errorResponses = {
        400: {"model": AnyErrorResponse, "description": 'Некорректный запрос'},
        422: {"model": CustomValidationErrorResponse, "description": 'Были введены некорректные значения параметров'},
        500: {"model": AnyErrorResponse, "description": 'Произошла непредвиденная ошибка'},
        401: {"model": AuthExceptionResponse, "description": 'Ошибка авторизации'}
    }

    router.include_router(
        auth.router,
        responses=errorResponses
    )

    # Теперь все функции-endpoints используют эти зависимости и дополнительно такие модели ответа
    router.include_router(
        limsClient.router, 
        dependencies=[Depends(auth.verify_token)],
        responses=errorResponses
    )

    router.include_router(
        statistics.router, 
        dependencies=[Depends(auth.verify_token)]
    )

    router.include_router(
        arshin.router,
        dependencies=[Depends(auth.verify_token)],
        responses=errorResponses
    )
    app.include_router(router)
    return app