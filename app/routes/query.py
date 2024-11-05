from fastapi import APIRouter, HTTPException
from app.schemas import QueryRequest, UpdateRetrieverRequest, UpdateModelRequest
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


@router.get("/get_current_model/")
async def get_current_model():
    try:
        current_model = assistant.llm.model
        return {"current_model": current_model}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/check_available_models/")
async def check_available_models():
    try:
        models = assistant.check_available_models()
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_current_retrievers/")
async def get_current_retrievers():
    try:
        retrievers = assistant.get_current_retrievers()
        return {"retrievers": retrievers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update_retriever/")
async def update_retriever_endpoint(request: UpdateRetrieverRequest):
    retrievers = await assistant.update_retriever(request.vectorstores)

    return {"status": "success", "current_retrievers": retrievers}


@router.post("/update_llm/")
async def update_model(request: UpdateModelRequest):
    try:
        model_name = assistant.update_llm(request.llm_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"status": "success", "current_model": model_name}
