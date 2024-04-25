from fastapi import APIRouter, Form, Request, Response, Cookie, HTTPException, status
from fastapi.responses import HTMLResponse
from config import TEMPLATES, BASE_URL

import aiohttp
router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return TEMPLATES.TemplateResponse("auth.html", context={"request": request})

@router.post("/", response_class=HTMLResponse)
async def auth_form(
    request: Request,
    response: Response,
    login: str = Form(...),
    password: str = Form(...),
):
    
    headers={"Content-Type": "application/json", "Accept": "application/json"}
    data = {"doc": {"auth": {"login": login, "pass": password}}}

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(f"{BASE_URL}/b2_api_xml/ubki/auth", json=data) as result:

            if result.status != 200:       
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unauthorized",
                )
            data = await result.json()

    token = data["doc"]["auth"]["sessid"]
    print("TOKEN: ",token)

    response = TEMPLATES.TemplateResponse(
        name="send_data.html", 
        context={"request": request}
    )
    response.set_cookie(
        key="token", value=token, max_age=3600*24, 
        samesite='lax', domain='localhost'
    )
    return response
