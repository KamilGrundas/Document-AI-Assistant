from fastapi import APIRouter, HTTPException
from typing import Dict, List
from app.schemas import VectorstoresResponse
from app.utils.vectorstore import list_vectorstores, save_vectorstore

router = APIRouter(prefix="/vectorstore", tags=["vectorstore"])


@router.post("/save_vectorstore/")
async def save_vectorstore_endpoint(filename: str) -> Dict[str, str]:
    try:
        await save_vectorstore(filename)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.get("/list_vectorstores/", response_model=VectorstoresResponse)
async def get_vectorstores() -> Dict[str, List[str]]:
    return {"vectorstores": await list_vectorstores()}
