from pydantic import BaseModel

class Data(BaseModel):
    data: dict
    reqtype: str = "i"
    reqidout: str = ""
    reqreason: str = "0"
    delreason: str = ""