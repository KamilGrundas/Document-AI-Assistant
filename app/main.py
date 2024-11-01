from fastapi import FastAPI
from app.routes import documents, vectorstore, query

app = FastAPI()


app.include_router(vectorstore.router)
app.include_router(documents.router)
app.include_router(query.router)


@app.get("/")
async def root():
    return {"message": "HI!"}
