from . import Depends, APIRouter, get_postgres_session, AsyncSession
from app.schemas.statistics import FullParamValue, FullParamValuesResponse, StatisticsParams, StatisticsResponse
from app.services.statistics import StatisticsService

router = APIRouter()

@router.post('/imreciseSearch', response_model=FullParamValuesResponse)
async def imreciseSearch(payload: FullParamValue = Depends(), postgres_session: AsyncSession = Depends(get_postgres_session)):
    service = StatisticsService(postgres_session)
    return await service.get_10_ending_options(payload)

@router.post('/statistics', response_model=list[StatisticsResponse])
async def statistics(payload: StatisticsParams = Depends(), postgres_session: AsyncSession = Depends(get_postgres_session)):
    service = StatisticsService(postgres_session)
    return await service.get_statistics(payload)