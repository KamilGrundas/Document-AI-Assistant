from fastapi import APIRouter, HTTPException
from app.schemas import QueryRequest, UpdateQAChainRequest
from app.services.doc_query import DocQueryAssistant

router = APIRouter(prefix="/query", tags=["query"])

assistant = None


@router.on_event("startup")
async def startup_event():
    global assistant
    assistant = await DocQueryAssistant.create()


@router.post("/query/")
async def get_answer(request: QueryRequest):
    question = request.question
    try:
        answer = await assistant.get_answer(question)
        return {"question": request.question, "answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update_qa_chain/")
async def update_qa_chain_endpoint(request: UpdateQAChainRequest):
    try:
        await assistant.update_qa_chain(request.vectorstores)
        return {"status": "success", "message": "QA chain updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
