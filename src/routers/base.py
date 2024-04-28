from abc import ABC, abstractmethod
from typing import Any
import aiohttp

from ..config import BASE_URL


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
                if result.status != 200:
                    print("ERROR API: ", await result.json())
                    return {}
                print(await result.text())
                return await result.json()