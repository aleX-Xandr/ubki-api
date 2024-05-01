from abc import ABC, abstractmethod
from fastapi.responses import JSONResponse
from typing import Any
import aiohttp
import json
import requests


from ..config import BASE_URL

class BaseError:
    @staticmethod
    async def err_500(request, exc):
        return JSONResponse(
            status_code=500,
            content={
                "message": "Сталася помилка",
                "details": str(exc)
            }
        )

class BaseFormRouter(ABC):
    api_path: str
    headers: dict = {
        "Accept": "application/json", 
        "Content-Type": "application/json"
    }

    @abstractmethod
    async def render_form(self, **kwargs) -> Any:
        ...

    @abstractmethod
    async def process_form_data(self, **kwargs) -> Any:
        ...

    async def call_api(self, **kwargs) -> dict:
        url = f"{BASE_URL}/{self.api_path}"
        async with aiohttp.ClientSession(headers=self.headers) as s:
            async with s.post(url, **kwargs) as result:
                print("-"*10)
                print(json.dumps(kwargs.get('json', {})))
                print(await result.text())
                data = await result.json()
                if result.status != 200:
                    errors = []
                    for item in data["sentdatainfo"]["items"]:
                        if item["errtype"] == "CRITICAL":
                            errors.append(item["msg"])
                        print("ERROR API: ", item["errtype"], item["msg"])
                    # print("ERROR API: ", await result.json())
                    return {}
                return data