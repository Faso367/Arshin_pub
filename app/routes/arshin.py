from app.schemas.arshin import VriParams, VriResponseItem
from . import Depends, APIRouter, MainService, AsyncSession, get_postgres_session

router = APIRouter()

@router.post('/vri', response_model=list[VriResponseItem])
async def vri(
    request_params: VriParams = Depends(),
    postgres_session: AsyncSession = Depends(get_postgres_session)
    ):
    service = MainService(postgres_session)
    return await service.get_equipment(request_params)