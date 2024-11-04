import os
from fastapi import HTTPException
from app.utils.documents import load_document, split_document
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores.base import VectorStoreRetriever
from langchain.retrievers import EnsembleRetriever
from langchain_chroma import Chroma
from typing import Dict, List

EMBEDDINGS = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
VECTORESTORE_FOLDER = "data/vectorstores"


async def save_vectorstore(filename: str) -> None:
    document = await load_document(filename)
    document = await split_document(document)
    vectorstore_name = os.path.splitext(filename)[0]
    path = os.path.join(VECTORESTORE_FOLDER, vectorstore_name)
    Chroma.from_documents(document, EMBEDDINGS, persist_directory=path)


async def load_vectorestore(foldername: str) -> Chroma:
    path = os.path.join(VECTORESTORE_FOLDER, foldername)
    vectorstore = Chroma(persist_directory=path, embedding_function=EMBEDDINGS)
    return vectorstore


async def list_vectorstores() -> Dict[str, List[str]]:
    if not os.path.exists(VECTORESTORE_FOLDER):
        os.makedirs(VECTORESTORE_FOLDER)
    try:
        vectorstores = os.listdir(VECTORESTORE_FOLDER)
        vectorstores = [
            vectorstore
            for vectorstore in vectorstores
            if os.path.isdir(os.path.join(VECTORESTORE_FOLDER, vectorstore))
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An error occurred while listing folders: {str(e)}"
        )

    return vectorstores


def create_retriever(vectorstore: Chroma, name: str = "Unknown", k: int = 3,) -> VectorStoreRetriever:
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    retriever.metadata = {"source":name}
    return retriever


def combine_retrievers(retrievers: List[Chroma]) -> EnsembleRetriever:
    return EnsembleRetriever(retrievers=retrievers)
