# src/api/routes.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/hello")
def say_hello():
    return {"message": "Hello from Sensai-AI!"}
