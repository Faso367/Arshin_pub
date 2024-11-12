from . import (
    EquipmentInfo, UniqueMiModifications, UniqueMitNotations,
    UniqueMitNumbers, UniqueMitTitles, UniqueOrgTitles,
    get_uniqueTable_by_Colname, AsyncSession,
    and_, or_, desc, select
    
)
from app.schemas.limsClient import ClientParams, ClientResponseItem
from app.schemas.arshin import VriParams, VriResponseItem

class MainRepository(object):

    def __init__(self, postgresSession: AsyncSession):
        self.session = postgresSession

    async def get_equipment_from_postgres(self, params: ClientParams) -> list[ClientResponseItem]:
        '''Возвращает строки (по умолчанию одну) номер свидетельства, дату поверки, пригодность
            по заданной дате поверки, организации-поверителе, обозначению типа, заводскому номеру'''

        query = select(
            EquipmentInfo.result_docnum,
            EquipmentInfo.verification_date,
            EquipmentInfo.applicability
        ).join(UniqueMitTitles, EquipmentInfo.mit_titleId == UniqueMitTitles.id) \
        .join(UniqueOrgTitles, EquipmentInfo.org_titleId == UniqueOrgTitles.id) \
        .join(UniqueMitNumbers, EquipmentInfo.mit_numberId == UniqueMitNumbers.id) \
        .filter(EquipmentInfo.verification_date >= params.send_date,
                EquipmentInfo.mi_number == params.mi_number,
                UniqueOrgTitles.org_title == params.org_title,
                UniqueMitNumbers.mit_number == params.mit_number
                ).limit(params.rows_count)

        result_set = await self.session.execute(query)
        # Читаем все строки из ответа, маппим каждую строку в словарь, затем преобразуем его в pydantic модель 
        return list(ClientResponseItem.model_validate(row._mapping) for row in result_set.fetchall())

        #return items
        # ДЛЯ ОДНОЙ ЗАПИСИ
        # async with self.async_session() as session:
        #     result_set = await session.execute(query)
        #     dict_res = result_set.mappings().first()
        #     if not dict_res:
        #         return ClientResponseItem()  # Пустой экземпляр модели
        #     return ClientResponseItem.model_validate(dict_res)


    async def select_vri(self, params: VriParams) -> list[VriResponseItem]:
        '''Делает выборку по любым колнкам'''

        # Создаём условия для WHERE
        ANDexpressions = []
        ORexpressions = []
        
        kwargs = params.model_dump(exclude_none=True)
        # Пробегаемся по полученным параметрам
        for colName, val in kwargs.items():

            if colName in ['rows', 'sort', 'start', 'applicability', 'verification_date', 'valid_date']:
                continue  # rows и start обработаны ранее, остальные будут обработаны в JOIN и FILTER

            elif colName in ['org_title', 'mit_number', 'mit_title', 'mit_notation', 'mi_modification']:
                uniqueTable = await get_uniqueTable_by_Colname(colName)
                uniqueColumn = getattr(uniqueTable, colName)
                ANDexpressions.append(uniqueColumn.ilike(f"{val}"))

            elif colName in ['mi_number', 'result_docnum', 'year']:
                column = getattr(EquipmentInfo, colName) 
                ANDexpressions.append(column == val)
       
            # Если используется неточный поиск по неопределенным параметрам
            elif colName == 'search':
                # Только под ключом search хранится список
                for v in val:
                    ORexpressions.append(uniqueColumn.ilike(f"{v}"))
                    ORexpressions.append(EquipmentInfo.mi_number.ilike(f"{v}"))
                    ORexpressions.append(EquipmentInfo.result_docnum.ilike(f"{v}"))

        # Составляем тело Where условия
        combined_expression1 = and_(*ANDexpressions)
        combined_expression2 = or_(*ORexpressions)
        combined_expression = and_(combined_expression1, combined_expression2)

        query = select(
            EquipmentInfo.mi_number,
            EquipmentInfo.result_docnum,
            EquipmentInfo.verification_date,
            EquipmentInfo.valid_date,
            EquipmentInfo.applicability,
            UniqueOrgTitles.org_title,
            UniqueMitTitles.mit_title,
            UniqueMitNumbers.mit_number,
            UniqueMitNotations.mit_notation,
            UniqueMiModifications.mi_modification
        ).join(UniqueMitTitles, EquipmentInfo.mit_titleId == UniqueMitTitles.id) \
        .join(UniqueOrgTitles, EquipmentInfo.org_titleId == UniqueOrgTitles.id) \
        .join(UniqueMitNumbers, EquipmentInfo.mit_numberId == UniqueMitNumbers.id) \
        .join(UniqueMitNotations, EquipmentInfo.mit_notationId == UniqueMitNotations.id) \
        .join(UniqueMiModifications, EquipmentInfo.mi_modificationId == UniqueMiModifications.id) \
        .filter(combined_expression)

        if 'sort' in kwargs:
            sortColName, sortParam = kwargs['sort'].split(' ')
            if sortColName == 'mi_number':
                col = EquipmentInfo.mi_number
            elif sortColName == 'result_docnum':
                col = EquipmentInfo.result_docnum
            else:
                uniqueTable = await get_uniqueTable_by_Colname(sortColName)
                col = getattr(uniqueTable, sortColName)
            # Сортируем по убыванию
            if sortParam == 'desc':
                query = query.order_by(desc(col))
            # Сортируем по возрастанию
            else:
                query = query.order_by(col)

        # Дополняем условия ограничения выборки
        query = query.limit(kwargs['rows']).offset(kwargs['start'])

        result_set = await self.session.execute(query)

        # Читаем все строки из ответа, маппим каждую строку в словарь, затем преобразуем его в pydantic модель 
        return list(VriResponseItem.model_validate(row._mapping) for row in result_set.fetchall())