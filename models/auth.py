from pydantic import BaseModel
from utils.models import OrmBase

class LoginMessage(BaseModel):
    username: str
    password: str


class LoginResponseMessage(BaseModel):
    access_token: str