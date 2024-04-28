from pydantic import BaseModel

class Scope(BaseModel):
    num: int
    location: list[str]