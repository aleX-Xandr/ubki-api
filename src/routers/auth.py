from fastapi import Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from typing import Any

from .base import BaseFormRouter
from ..config import BASE_URL, DOMAIN, TEMPLATES


router = InferringRouter()

@cbv(router)
class AuthRouter(BaseFormRouter):
    api_path: str = "b2_api_xml/ubki/auth"

    async def get_token(self, login:str, password:str) -> str | None:
        json = {"doc": {"auth": {"login": login, "pass": password}}}
        data = await self.call_api(json=json)
        if data:
            return data["doc"]["auth"]["sessid"]

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
        
        token = await self.get_token(login, password)
        print(token)
        if not token:
            return RedirectResponse("/auth", status_code=302)

        response = RedirectResponse("/file", status_code=302)
        response.set_cookie(
            key="token", value=token, max_age=3600*24, 
            samesite='lax', domain=DOMAIN
        )
        return response
