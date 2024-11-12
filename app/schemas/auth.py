from . import BaseModel

class Token(BaseModel):
    access_token: str
    #refresh_token: str
    tokens_type: str = 'bearer'


class TokenData(BaseModel):
    token: str
    username: str
    expire: str

