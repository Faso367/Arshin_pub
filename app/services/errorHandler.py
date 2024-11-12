from functools import wraps
import redis.exceptions
from sqlalchemy.exc import SQLAlchemyError, OperationalError
import traceback
import os
import redis

class ServiceException(Exception):
    def __init__(self, *args, statusCode=500, orig_exc=None):
        super().__init__(*args)

        self.statusCode = statusCode
        
        # Сохраняем тип оригинального исключения
        self.original_exception_type = type(orig_exc).__name__ if orig_exc else "UnknownException"
        self.original_class_exception_type = str(type(orig_exc).__class__) if orig_exc else "UnknownClassException"
        # Извлекаем стек вызовов из оригинального исключения
        tb = traceback.extract_tb(orig_exc.__traceback__) if orig_exc else []
        
        formatted_trace = []
        
        for frame in tb[1:]:  # Исключаем последний вызов (например, wrapper)
            # Проверяем, чтобы путь не содержал стандартных библиотечных директорий
            if "site-packages" not in frame.filename and "lib" not in frame.filename:
                # Оставляем последние два элемента пути
                folder, filename = os.path.split(os.path.dirname(frame.filename)), os.path.basename(frame.filename)
                short_path = os.path.join(folder[-1], filename)
                formatted_trace.append(f"{short_path}, line {frame.lineno}, in {frame.name}")
        
        self.stack_trace = "\n".join(formatted_trace) if formatted_trace else "No traceback available"
    
    
    def __str__(self):
        message  = 'Вернулась ошибка без аргументов'
        if len(self.args) >= 2:
            message = self.args[0] + self.args[1]
        else:
            message = self.args[0]
        return (f"{self.original_exception_type} -> ServiceException: {message}\n"
                f"Class of exception: {self.original_class_exception_type}\n"
                f"Traceback:\n{self.stack_trace}")

def handle_main_repo_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except SQLAlchemyError as e:
            raise ServiceException("Ошибка при создании контекста или при выполнении запроса к БД", orig_exc=e)
        except OperationalError as e:
            raise ServiceException("Ошибка соединения с Postgres", orig_exc=e)
        except Exception as e:
            raise ServiceException("Непредвиденное исключение", orig_exc=e)
    return wrapper


def handle_auth_repo_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except redis.exceptions.ConnectionError as e:
            raise ServiceException('Ошибка соединения с Redis', orig_exc=e)
        except Exception as e:
            raise ServiceException("Непредвиденное исключение", orig_exc=e)
    return wrapper