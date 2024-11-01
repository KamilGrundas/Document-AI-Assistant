from fastapi import APIRouter
from app.models import QueryRequest


router = APIRouter(prefix="/query", tags=["query"])
