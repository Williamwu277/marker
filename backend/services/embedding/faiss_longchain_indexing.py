import faiss 

from uuid import uuid4
from langchain_core.documents import Document
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS


class FAISS_INDEX:
    def __init__(self):
        self.vector_store = FAISS