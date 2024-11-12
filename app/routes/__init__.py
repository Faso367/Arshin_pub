from fastapi import Depends, APIRouter, Form
from typing import Annotated
import jwt
from app.services.main import MainService
from sqlalchemy.ext.asyncio import AsyncSession
from app.startups.db import get_postgres_session