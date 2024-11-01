from fastapi import FastAPI
from app.routes import documents, vectorstore

app = FastAPI()


app.include_router(vectorstore.router)
app.include_router(documents.router)


@app.get("/")
async def root():
    return {"message": "HI!"}
