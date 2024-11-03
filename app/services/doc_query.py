from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.chains.retrieval_qa.base import RetrievalQA
from app.utils.vectorstore import (
    create_retriever,
    combine_retrievers,
    load_vectorestore,
    list_vectorstores,
)
from typing import List, Tuple, Dict
from collections import defaultdict

TEMPLATE = """
Answer the following question based on the provided context. If you don't know the answer, reply with "I don't know."

{context}

Question: {question}

Answer:
"""

PROMPT = PromptTemplate(
    template=TEMPLATE, input_variables=["context", "question"]
)


class DocQueryAssistant:
    def __init__(self, llm, retriever):
        self.llm = llm
        self.retriever = retriever
        self.qa_chain = self.create_qa_chain()

    @classmethod
    async def create(cls):
        llm = OllamaLLM(model="llama3.2")
        vectorstores = await list_vectorstores()
        retriever = await cls.load_retriever(vectorstores) if vectorstores else None
        return cls(llm, retriever)

    @staticmethod
    async def load_retriever(vectorstores: List[str]):
        retrievers = [
            create_retriever(await load_vectorestore(foldername), foldername)
            for foldername in vectorstores if foldername in await list_vectorstores()
        ]
        retriever = combine_retrievers(retrievers) if retrievers else None
        return retriever

    def create_qa_chain(self):
        qa_chain = (
            RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.retriever,
                return_source_documents=True,
                chain_type_kwargs={"prompt": PROMPT},
            )
            if self.retriever
            else None
        )
        return qa_chain

    async def update_retriever(self, vectorstores: List[str]):
        self.retriever = await self.load_retriever(vectorstores)
        if self.qa_chain and self.retriever:
            self.qa_chain.retriever = self.retriever
        else:
            self.qa_chain = self.create_qa_chain()
        return self.retriever.retrievers if self.retriever else []

    def create_prompts(self, question: str, documents: List) -> Tuple[Dict, Dict]:
        documents_by_source = defaultdict(list)
        for doc in documents:
            source_file = doc.metadata.get("source", "Unknown Source")
            documents_by_source[source_file].append(doc.page_content)

        prompts_by_source = {}
        for source_file, contents in documents_by_source.items():
            context = "\n".join(contents)
            prompt = f"""
            Answer the following question based on the provided context. If the content does not provide an answer, you may write "I don't know".          
            {source_file[10:]}: `{context}`\n\nQuestion: {question}\nAnswer:"""
            prompts_by_source[source_file] = prompt

        return prompts_by_source, documents_by_source

    async def get_answer(self, question: str) -> str:
        if self.qa_chain is None:
            raise Exception("The QA chain has not been initialized.")
        # Single request to the model
        return self.qa_chain.invoke(question)

    async def get_splitted_answer(self, question: str) -> Dict:
        if not self.retriever:
            raise Exception("Retriever has not been initialized.")

        documents = self.retriever.invoke(question)
        prompts, documents_by_source = self.create_prompts(question, documents)

        # Multiple requests to the model
        answers_by_source = {
            source_file: self.llm.invoke(prompt)
            for source_file, prompt in prompts.items()
        }
        formatted_answer = "\n\n".join(
            f"{source_file[10:]}:\n{answer}"
            for source_file, answer in answers_by_source.items()
        )

        return {
            "answer": formatted_answer,
            "source_files": list(documents_by_source.keys()),
        }
