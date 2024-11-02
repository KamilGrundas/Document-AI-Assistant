from langchain_ollama import OllamaLLM
from app.utils.vectorstore import (
    create_retriever,
    combine_retrievers,
    load_vectorestore,
    list_vectorstores,
)
from typing import List, Tuple, Dict
from collections import defaultdict



class DocQueryAssistant:
    def __init__(self, llm, retriever):
        self.llm = llm
        self.retriever = retriever

    @classmethod
    async def create(cls):
        llm = OllamaLLM(model="llama3.2")
        vectorstores = await list_vectorstores()
        retriever = await cls.load_retriever(vectorstores) if vectorstores else None
        return cls(llm, retriever)

    @staticmethod
    async def load_retriever(vectorstores: List[str]):
        retrievers = [create_retriever(await load_vectorestore(foldername)) for foldername in vectorstores]
        return combine_retrievers(retrievers)

    async def update_retriever(self, vectorstores: List[str]):
        self.retriever = await self.load_retriever(vectorstores)

    def create_prompts(self, question: str, documents: List) -> Tuple[Dict, Dict]:
        documents_by_source = defaultdict(list)
        for doc in documents:
            source_file = doc.metadata.get("source_file", "Unknown Source")
            documents_by_source[source_file].append(doc.page_content)

        prompts_by_source = {}
        for source_file, contents in documents_by_source.items():
            context = "\n".join(contents)
            prompt = f"""
            Answer the following question based on the provided context. If the content does not provide an answer, you may write "I don't know".
            Context: `{context}`\n\nQuestion: {question}\nAnswer:"""
            prompts_by_source[source_file] = prompt

        return prompts_by_source, documents_by_source
    
    # async def get_answer(self, question: str) -> Dict:
    #     if not self.retriever:
    #         raise Exception("Retriever has not been initialized.")
        
    #     documents = self.retriever.invoke(question)
    #     full_context = "\n".join(doc.page_content for doc in documents)

    #     print(full_context)

    #     prompt = f"""
    #     Answer the following question based on the provided context. If the content does not provide an answer, you may write "I don't know".
    #     Contexts: `{full_context}`\n\nQuestion: {question}\nAnswer:"""

    #     # Single request to the model
    #     answer = self.llm.invoke(prompt)
        

    #     return {
    #         "answer": answer
    #     }

    async def get_splitted_answer(self, question: str) -> Dict:
        if not self.retriever:
            raise Exception("Retriever has not been initialized.")
        
        documents = self.retriever.invoke(question)
        prompts, documents_by_source = self.create_prompts(question, documents)

        # Multiple requests to the model
        answers_by_source = {source_file: self.llm.invoke(prompt) for source_file, prompt in prompts.items()}
        formatted_answer = "\n\n".join(f"{source_file}:\n{answer}" for source_file, answer in answers_by_source.items())

        return {
            "answer": formatted_answer,
            "source_files": list(documents_by_source.keys())
        }