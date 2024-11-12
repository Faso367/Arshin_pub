from app.repositories.statistics import StatisticsRepository
from app.schemas.statistics import FullParamValue, FullParamValuesResponse, StatisticsParams, StatisticsResponse
from .errorHandler import handle_main_repo_errors
from sqlalchemy.ext.asyncio import AsyncSession

class StatisticsService:
    def __init__(self, postgressSession: AsyncSession):
        self.statisticsRepo = StatisticsRepository(postgressSession)

    @handle_main_repo_errors
    async def get_10_ending_options(self, param: FullParamValue) -> FullParamValuesResponse:
        return await self.statisticsRepo.search_full_param_values(param.paramName, param.value)

    @handle_main_repo_errors
    async def get_statistics(self, params: StatisticsParams) -> list[StatisticsResponse]:
        return await self.statisticsRepo.select_statistics_for_one_value(params)