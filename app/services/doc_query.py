from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
from app.utils.vectorstore import (
    create_retriever,
    combine_retrievers,
    load_vectorestore,
    list_vectorstores,
)
from typing import List

TEMPLATE = """
Answer the following question based on the provided context. If you don't know the answer, reply with "I don't know."

{context}

Question: {question}

Answer:
"""

PROMPT = PromptTemplate(template=TEMPLATE, input_variables=["context", "question"])


class DocQueryAssistant:
    def __init__(self, llm, qa_chain):
        self.llm = llm
        self.qa_chain = qa_chain

    @classmethod
    async def create(cls):
        llm = OllamaLLM(model="llama3.2")
        vectorstores = await list_vectorstores()
        if vectorstores:
            retriever = await cls.load_retriever(vectorstores)
            qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=False,
                chain_type_kwargs={"prompt": PROMPT},
            )
        else:
            qa_chain = None
        return cls(llm, qa_chain)

    @staticmethod
    async def load_retriever(vectorstores: List[str]):
        retrievers = []

        for foldername in vectorstores:
            vectorstore = await load_vectorestore(foldername)
            retriever = create_retriever(vectorstore)
            retrievers.append(retriever)

        combined_retriever = combine_retrievers(retrievers)
        return combined_retriever

    async def update_qa_chain(self, vectorstores: List[str]):
        retriever = await self.load_retriever(vectorstores)
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=False,
            chain_type_kwargs={"prompt": PROMPT},
        )

    async def get_answer(self, question: str) -> str:
        if self.qa_chain is None:
            raise Exception("The QA chain has not been initialized.")
        return self.qa_chain.invoke(question)
