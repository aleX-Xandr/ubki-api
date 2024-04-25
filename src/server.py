from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from routers.root import router

app = FastAPI(title="My FastAPI App", description="A simple FastAPI application")

origins = ["http://localhost:8000"]  # Change to your frontend domain if needed

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # This allows cookies
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(router, tags=["Main"])