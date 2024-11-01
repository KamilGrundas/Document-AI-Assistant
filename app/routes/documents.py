from fastapi import APIRouter, File, UploadFile
from typing import Dict, List
from app.schemas import UploadFileResponse, DocumentsResponse
from app.utils.documents import save_pdf_file, list_files

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload_document/", response_model=UploadFileResponse)
async def upload_document(file: UploadFile = File(...)) -> Dict[str, str]:
    return await save_pdf_file(file)


@router.get("/list_documents/", response_model=DocumentsResponse)
async def get_documents() -> Dict[str, List[str]]:
    return await list_files()
