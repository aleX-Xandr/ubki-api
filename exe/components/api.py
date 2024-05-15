from dataclasses import dataclass, field

import requests

from config import BASE_URL

@dataclass
class Client:
    api_path: str
    headers: dict = field(default_factory=lambda: {
        "Accept": "application/json",
        "Content-Type": "application/json"
    })

    def call_api(self, **kwargs) -> tuple[int, dict]:
        url = f"{BASE_URL}/{self.api_path}"
        result = requests.post(
            url, headers=self.headers, **kwargs
        )
        print(result.text)
        return result
            
    def authorize(self, login, password) -> dict:
        result = self.call_api(
            json={"doc": {"auth": {"login": login, "pass": password}}}
        )
        return result.json()
        
    def send_data(self, data) -> tuple[int, dict]:
        result = self.call_api(
            json=data
        )
        return result.status_code, result.json()
