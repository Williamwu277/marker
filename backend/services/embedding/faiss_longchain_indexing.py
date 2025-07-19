import faiss 

from uuid import uuid4
from langchain_core.documents import Document
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS


class FAISS_INDEX:
    def __init__(self, embedding_length=1024):
        self.embedding_length = embedding_length
        self.faiss_index = faiss.IndexFlatL2(embedding_length)
        self.vector_store = FAISS(
           
        )