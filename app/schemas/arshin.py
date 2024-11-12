from . import datetime, date, Optional, Field, BaseModel, field_validator, model_validator

current_year = datetime.now().year
exactSearchParams = ['mit_number', 'mi_number', 'org_title', 'mit_title', 'mit_title', 'mi_modification', 'result_docnum']


class VriResponseItem(BaseModel):
    mi_number: str
    result_docnum: str
    verification_date: Optional[date] = None
    valid_date: Optional[date] = None
    applicability: bool
    org_title: str
    mit_title: str
    mit_number: str
    mit_title: str
    mi_modification: str


class VriParams(BaseModel):
    sort: str | None = None
    year: int = Field(current_year, ge=2019, le=current_year, description=f'Параметр year может принимать значения от 2019 до {current_year}')
    rows: int = Field(10, ge=1, le=100, description='Параметр rows может принимать значения от 1 до 100')
    start: int = Field(0, ge=0, le=99999, description='Параметр start может принимать значения от 0 до 99999')
    applicability: bool | None = None
    result_docnum: str | None = None
    mit_number: str | None = None
    mi_number: str | None = None
    verification_date: date | None = None
    valid_date: date | None = None
    org_title: str | None = None
    mit_title: str | None = None
    mit_title: str | None = None
    mi_modification: str | None = None

    @field_validator('verification_date', 'valid_date', mode='before')
    def validate_date_format(cls, value: str):
        if value is None:  # Если значение не задано, пропускаем валидацию
            return value
        try:
            return date.fromisoformat(value)  # Формат yyyy-MM-dd
        except ValueError:
            raise ValueError("Даты указываются в формате yyyy-MM-dd")

    @field_validator('sort')
    def validate_sort(cls, value: str | None):
        if value is None:  # Если значение не задано, пропускаем валидацию
            return value
        value = value.replace('%20', ' ').replace('+', ' ')
        parts = value.split(' ')
        if len(parts) != 2 or parts[-1].lower() not in ['asc', 'desc']:
            raise ValueError("Параметр sort имеет такой формат: аттрибут+asc или аттрибут+desc")
        elif parts[0] not in exactSearchParams:
            raise ValueError(f"Атрибут {parts[0]} недоступен для сортировки")
        return "".join(value)

    @model_validator(mode='before')
    def check_exclusive_fields(cls, values):

        searchWasFind = False
        countExactParams = 0
        for key, val in values.items():
            if key == 'search':
                searchWasFind = True
            elif key in exactSearchParams:
                countExactParams += 1

        if countExactParams > 0 and searchWasFind:
            raise ValueError("Нельзя одновременно использовать неточный поиск и поиск по конкретным параметрам")

        return values
    
    @model_validator(mode='after')
    def validate_atts(cls, model):
        '''Заменяем спецсимволы для неточного поиска по БД'''
        
        data = model.model_dump(exclude_none=True)
        for key, value in data.items():
            if (key == 'result_docnum' or key == 'mi_number') and ('*' in value or ' ' in value):
                raise ValueError("Параметры result_docnum и mi_number не поддерживают неточный поиск")
            # Если это поле типа string, поддерживающее неточный поиск
            elif isinstance(value, str):
                if value == '' or value.isspace():
                    raise ValueError(f"Значение параметра {key} не может быть пустой строкой")
                data[key] = value.replace('*', '%').replace('?', ' ')
        # Обновляем модель с модифицированными значениями
        return data