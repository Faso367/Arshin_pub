from sqlalchemy.future import select
# Импортирую явно, тк по относительному пути через globals() не получится найти эти классы
from app.models.postgres import UniqueMitTitles, UniqueMitNotations, UniqueMiModifications, UniqueMitNumbers, UniqueOrgTitles, EquipmentInfo
#from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc, and_, or_, func
from redis import Redis, ConnectionPool
from redis.commands.json.path import Path
#from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import AsyncSession


async def get_uniqueTable_by_Colname(uniqueColumnName):
    '''Возвращает объект одной из пяти моделей уникальных таблиц по имени колонки'''

    tables_mainCols = {
        'UniqueMitTitles': 'mit_title',
        'UniqueMitNotations': 'mit_notation',
        'UniqueMiModifications': 'mi_modification',
        'UniqueMitNumbers': 'mit_number',
        'UniqueOrgTitles': 'org_title'
    }
    for tableName, colName in tables_mainCols.items():
        if uniqueColumnName == colName:
            uniqueTable = globals()[tableName]
            return uniqueTable
    return ''