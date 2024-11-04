from fastapi import APIRouter, HTTPException
from app.schemas import QueryRequest, UpdateQAChainRequest
from app.services.doc_query import DocQueryAssistant

router = APIRouter(prefix="/query", tags=["query"])

assistant = None


@router.on_event("startup")
async def startup_event():
    global assistant
    assistant = await DocQueryAssistant.create()


@router.post("/query_single/")
async def get_answer(request: QueryRequest):
    question = request.question
    try:
        answer = await assistant.get_answer(question)
        return answer
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query_split/")
async def get_splitted_answer(request: QueryRequest):
    question = request.question
    try:
        answer = await assistant.get_splitted_answer(question)
        return answer
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/check_availabe_models/")
async def check_availabe_models():
    try:
        models = assistant.check_available_models()
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update_retriever/")
async def update_retriever_endpoint(request: UpdateQAChainRequest):

    retrievers = await assistant.update_retriever(request.vectorstores)
    loaded_retrievrs = [retriever.metadata.get("source") for retriever in retrievers]

    return {"status": "success", "current_retrievers": loaded_retrievrs}
