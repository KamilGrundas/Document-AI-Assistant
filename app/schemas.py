from pydantic import BaseModel
from typing import List


class UploadFileResponse(BaseModel):
    filename: str


class DocumentsResponse(BaseModel):
    documents: List[str]


class VectorstoresResponse(BaseModel):
    vectorstores: List[str]


class QueryRequest(BaseModel):
    question: str
