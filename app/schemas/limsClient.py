from . import Field, date, field_serializer, BaseModel, field_validator, json

class ClientParams(BaseModel):
    send_date: date = Field(description="Даты указываются в формате yyyy-mm-dd")
    mi_number: str
    mit_number: str
    org_title: str
    rows_count: int = Field(1, ge=1, le=5, description='Параметр rows может принимать значения от 1 до 5')

    # Настройка сериализации поля send_date
    @field_serializer('send_date')
    def serialize_send_date(self, value: date) -> str:
        return value.isoformat()

    @field_validator("mi_number", "mit_number", "org_title")
    def non_empty_string(cls, value):
        if not value.strip():
            raise ValueError("Значение не должно быть пустой строкой")
        return value

    def model_dump(self, *args, **kwargs):
        original_dump = super().model_dump(*args, **kwargs)
        if isinstance(original_dump['send_date'], date):
            original_dump['send_date'] = original_dump['send_date'].isoformat()
        return json.dumps(original_dump)
    

class ClientResponseItem(BaseModel):
    result_docnum: str | None = None
    verification_date: date | None = None
    applicability: bool | None = None

    @field_serializer('verification_date')
    def serialize_send_date(self, value: date | None) -> str:
        if value == None:
            return None
        return value.isoformat()