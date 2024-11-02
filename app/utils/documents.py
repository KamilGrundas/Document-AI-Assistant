from fastapi import HTTPException, File
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents.base import Document
from typing import List, Dict
import os

DOCS_FOLDER = "data/docs"


async def save_pdf_file(file: File) -> Dict[str, str]:
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    os.makedirs(DOCS_FOLDER, exist_ok=True)

    file_location = os.path.join(DOCS_FOLDER, file.filename)

    if os.path.exists(file_location):
        base_name, extension = os.path.splitext(file.filename)
        counter = 1
        while os.path.exists(file_location):
            new_filename = f"{base_name}_{counter}{extension}"
            file_location = os.path.join(DOCS_FOLDER, new_filename)
            counter += 1

    try:
        with open(file_location, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An error occurred while saving the file: {str(e)}"
        )

    return {"filename": os.path.basename(file_location)}


async def list_files() -> List[str]:
    if not os.path.exists(DOCS_FOLDER):
        os.makedirs(DOCS_FOLDER)
    try:
        documents = os.listdir(DOCS_FOLDER)
        documents = [
            file
            for file in documents
            if os.path.isfile(os.path.join(DOCS_FOLDER, file))
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An error occurred while listing files: {str(e)}"
        )

    return documents


async def load_document(filename: str) -> List[Document]:
    path = os.path.join(DOCS_FOLDER, filename)
    loader = PyPDFLoader(path)
    document = loader.load()
    return document


async def split_document(document: List[Document]) -> RecursiveCharacterTextSplitter:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
    )
    return text_splitter.split_documents(document)
