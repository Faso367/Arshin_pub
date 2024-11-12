from fastapi.responses import ORJSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from app.services.logging import Logger
from app.schemas.error import AuthException
from app.schemas.limsClient import ClientParams
from app.services.errorHandler import ServiceException
from fastapi import Request

# Перехват исключений для входных и выходных параметров
async def validation_exception_handler(request, exc: RequestValidationError):
    messages = []
    for error in exc.errors():
        field = error['loc'][-1]
        message = error['msg']
        
        # Проверяем, если ошибка связана с `send_date`, добавляем описание
        if field == 'send_date':
            description = ClientParams.model_fields['send_date'].description
            message = description
        
        messages.append(f"{field}: {message}")
    return ORJSONResponse(
        status_code = 422,
        content={'messages': messages})

async def custom_validation_exception_handler(request: Request, exc: ValueError):
    messages = []
    for error in exc.errors():
        field = error['loc'][-1]
        message = error['msg']
        messages.append(f"{field}: {message.split(',')[-1]}")
    return ORJSONResponse(
        status_code = 422,
        content={'messages': messages})


# Перехват любых исключений (сервисы (+ репозитории), аутентификация и тд)
class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, dispatch = None):
        self.logService = Logger().logger
        super().__init__(app, dispatch)
    async def dispatch(self, request, call_next):
        try:
            response = await call_next(request)
            return response
        except AuthException as e:
            return ORJSONResponse(
                status_code = 401,
                content =
                {
                    'message': e.message,
                    'headers': {"WWW-Authenticate": "Bearer"}
                }
            )
        except ServiceException as e:
            self.logService.error(str(e))
            return ORJSONResponse(
                status_code=500,
                content={'message': 'Возникла непредвиденная ошибка'}
            )
        
        except Exception as exc:
            self.logService.error(f"Непредвиденная ошибка: {str(exc.args)}", exc_info=True)
            return ORJSONResponse(
                status_code=500,
                content={'message': 'Возникла непредвиденная ошибка'}
            )