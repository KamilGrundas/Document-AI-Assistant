from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import documents, vectorstore, query, views

app = FastAPI()

# app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(views.router)
app.include_router(vectorstore.router)
app.include_router(documents.router)
app.include_router(query.router)
