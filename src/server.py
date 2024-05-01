from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .routers import *
from . import config

origins = ["http://localhost:8000"]
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    app=StaticFiles(directory=f"{config.WORK_DIR}static"), 
    name="static",
    path="/static", 
)

# app.add_exception_handler(Exception, base.BaseError.err_500)
app.include_router(auth.router, tags=["Auth", "Form"])
app.include_router(file.router, tags=["File", "Form"])