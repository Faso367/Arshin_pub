from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .startups.routesStartup import init_routes
from .startups.db import init_db
from fastapi.exceptions import RequestValidationError

from .exceptions.exceptionHandlers import (
    validation_exception_handler,
    custom_validation_exception_handler,
    ErrorHandlingMiddleware
    #internal_server_error_handler,
)

defaultApp = FastAPI(
    lifespan=init_db,
    default_response_class=ORJSONResponse
)
app = init_routes(defaultApp)

app.add_exception_handler(ValueError, custom_validation_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.add_middleware(ErrorHandlingMiddleware)
