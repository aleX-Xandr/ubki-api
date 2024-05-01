from datetime import datetime
from fastapi import Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from typing import Any

from .base import BaseFormRouter
from ..config import BASE_URL, DOMAIN, TEMPLATES

import pytz


router = InferringRouter()

@cbv(router)
class AuthRouter(BaseFormRouter):
    api_path: str = "b2_api_xml/ubki/auth"

    async def get_token(self, login:str, password:str) -> str | None:
        json = {"doc": {"auth": {"login": login, "pass": password}}}
        data = await self.call_api(json=json)
        if data:
            return data["doc"]["auth"] # {"sessid":"902E49F88B274CCE9105599E25653933","datecr":"29.04.2024 10:40","dateed":"30.04.2024 2:00","userlogin":"123456789QQQqqq","userid":"9901248","userfname":"Валерія","userlname":"Огаркова","usermname":"Володимирівна","rolegroupid":"5","rolegroupname":"","agrid":"13128","agrname":"ФІНАНСОВА КОМПАНІЯ СІТІ ФІНАНС","role":"12","mustchngpass":"0"}

    @router.get("/", response_class=HTMLResponse, response_model=None)
    @router.get("/auth", response_class=HTMLResponse, response_model=None)
    def render_form(self, request: Request) -> Any:
        return TEMPLATES.TemplateResponse("auth.html", context={"request": request})
    
    @router.post("/auth", response_class=RedirectResponse, response_model=None)
    async def process_form_data(
        self,
        login:str = Form(...),
        password:str = Form(...),
    ) -> Any:
        
        resp = await self.get_token(login, password)
        print(resp)

        if not resp:
            return RedirectResponse("/auth", status_code=302)
        if "errcode" in resp:
            HTTPException(status_code=500, detail=resp["errtext"])
        if "sessid" not in resp or "dateed" not in resp:
            raise HTTPException(status_code=401, detail="Помилка авторизації")

        dateed_local = datetime.strptime(resp["dateed"], "%d.%m.%Y %H:%M")
        dateed_delta = dateed_local - datetime.now()

        response = RedirectResponse("/file", status_code=302)
        response.set_cookie(
            key="token", value=resp["sessid"], expires=dateed_delta.total_seconds(), 
            samesite='lax', domain=DOMAIN
        )
        return response
        
