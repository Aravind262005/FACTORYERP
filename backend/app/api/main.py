from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load env before importing routes so globals can see the API key
load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))
load_dotenv() # Also try cwd

from app.api.routes import router

app = FastAPI(title="Manufact AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
