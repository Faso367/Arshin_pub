from . import (
    UniqueMitTitles, UniqueMitNotations, UniqueMiModifications,
    UniqueMitNumbers, UniqueOrgTitles, EquipmentInfo,
    AsyncSession, select,
    and_, or_, func, get_uniqueTable_by_Colname
)
from app.schemas.statistics import FullParamValuesResponse, StatisticsParams, StatisticsResponse

class StatisticsRepository(object):

    def __init__(self, postgresSession: AsyncSession):
        self.session = postgresSession

    async def search_full_param_values(self, colName, searchVal) -> FullParamValuesResponse:
        '''Получает на вход имя колонки и находит 10 вариантов полных значений для этой колонки'''

        # Получаем объект нужной уникальной колонки
        uniqueTable = await get_uniqueTable_by_Colname(colName)
        uniqueColumn = getattr(uniqueTable, colName)

        query = select(uniqueColumn).filter(uniqueColumn.ilike(f'%{searchVal}%')).limit(10)
        result_set = await self.session.execute(query)
        res = result_set.scalars().all()
        res = FullParamValuesResponse(paramValues=res)
        return res


    async def select_statistics_for_one_value(self, params: StatisticsParams) -> list[StatisticsResponse]:
        '''Возвращает список записей: количество найденных записей и год (в котором искали)'''
        ANDexpressions = []
        ORexpressions = []
        
        q = select(
            func.count(EquipmentInfo.id),
            EquipmentInfo.year
        )

        for colName, val in params.model_dump(exclude_none=True).items():
            uniqueTable = await get_uniqueTable_by_Colname(colName)
            idColumn = getattr(EquipmentInfo, colName + 'Id')
            mainColumn = getattr(uniqueTable, colName)
            ANDexpressions.append(mainColumn == val)
            q = q.join(uniqueTable, uniqueTable.id == idColumn)

        # Составляем тело Where условия
        combined_expression1 = and_(*ANDexpressions)
        combined_expression2 = or_(*ORexpressions)
        combined_expression = and_(combined_expression1, combined_expression2)

        q = q.filter(combined_expression)
        q = q.group_by(EquipmentInfo.year)

        # Выполняем запрос
        result_set = await self.session.execute(q)
        return list(StatisticsResponse(count=row[0], year=row[1]) for row in result_set.fetchall())