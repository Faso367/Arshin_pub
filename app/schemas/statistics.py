from pydantic import BaseModel, model_validator, field_validator

class StatisticsParams(BaseModel):
    mit_number: str | None = None
    mit_title: str | None = None
    mit_notation: str | None = None
    mi_modification: str | None = None

    @model_validator(mode='after')
    def check_exclusive_fields(cls, model):
        data = model.model_dump(exclude_none=True)
        non_empty_fields = dict((key, value) for key, value in data.items() if value != '' and value is not None)
        return non_empty_fields


class StatisticsResponse(BaseModel):
    count: int
    year: int


class FullParamValue(BaseModel):
    paramName: str
    value: str

    @field_validator('paramName')
    def validate_param(cls, name: str):
        if name not in ['mit_number', 'mit_title', 'mit_notation', 'mi_modification']:
            raise ValueError(f"Задано некорректное значение искомого параметра")
        return name
    
    
class FullParamValuesResponse(BaseModel):
    paramValues: list[str]