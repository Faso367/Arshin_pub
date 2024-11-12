from app.repositories.main import MainRepository
from app.schemas.arshin import VriResponseItem, VriParams
from app.schemas.limsClient import ClientParams, ClientResponseItem
from .errorHandler import handle_main_repo_errors
from sqlalchemy.ext.asyncio import AsyncSession

class MainService:
    def __init__(self, postgressSession: AsyncSession):
        self.mainRepo = MainRepository(postgressSession)

    @handle_main_repo_errors
    async def get_client_equipment(self, params: ClientParams) -> list[ClientResponseItem]:
        return await self.mainRepo.get_equipment_from_postgres(params)
    
    @handle_main_repo_errors
    async def get_equipment(self, params: VriParams) -> list[VriResponseItem]:
        return await self.mainRepo.select_vri(params)