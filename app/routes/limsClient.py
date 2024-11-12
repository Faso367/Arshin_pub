from app.schemas.limsClient import ClientParams, ClientResponseItem
from . import Depends, APIRouter, MainService, get_postgres_session
from sqlalchemy.ext.asyncio import AsyncSession
router = APIRouter()

@router.post('/checkEquipment', response_model=list[ClientResponseItem] | None)
async def checkEquipment(
    request_params: ClientParams = Depends(),
    postgres_session: AsyncSession = Depends(get_postgres_session)
    ):
    '''Вызывается пользователем с заданными параметрами''' 
    service =  MainService(postgres_session)
    return await service.get_client_equipment(request_params)