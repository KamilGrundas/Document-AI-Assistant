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


class UpdateRetrieverRequest(BaseModel):
    vectorstores: List[str]


class UpdateModelRequest(BaseModel):
    llm_name: str
