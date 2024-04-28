from fastapi import Request, File, UploadFile, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from typing import Any
import pandas as pd
import io

from .base import BaseFormRouter
from ..config import TEMPLATES
from ..models.builder import DataBuilder 

import asyncio


router = InferringRouter()

@cbv(router)
class FormRouter(BaseFormRouter):
    api_path: str = "upload/data"

    async def build_task(self, csv_dict: dict):
        builder = DataBuilder(csv_dict)
        await builder.build()
        print(builder.as_dict)
        data = await self.call_api(json=builder.as_dict)
        print(data)
        if data:
            return data["doc"]["auth"]["sessid"]
    
    @router.get("/file", response_class=HTMLResponse, response_model=None)
    async def render_form(
        self,
        request: Request,
    ) -> Any:
        return TEMPLATES.TemplateResponse(
            name="file.html", 
            context={"request": request}
        )

    @router.post("/file", response_class=RedirectResponse, response_model=None)
    async def process_form_data(
        self,
        request: Request,
        token: str = Cookie(default="aaaa"), # None),
        file: UploadFile = File(...)
    ) -> Any:
        if not token:
            return RedirectResponse("/auth", status_code=302)
        try:
            content = await file.read()
            buffer = io.BytesIO(content)
            csv_data = pd.read_csv(buffer, encoding="Windows-1251", sep=";")
            csv_dicts = csv_data.to_dict(orient='records')
            for csv_dict in csv_dicts:
                asyncio.create_task(self.build_task(csv_dict))

            message = "Додано успiшно!"
        except Exception as e:
            message = f"Помилка: {str(e)}"
        return TEMPLATES.TemplateResponse(
            name="file.html", 
            context={"request": request, "message": message}
        )