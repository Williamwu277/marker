import faiss 
import twelvelabs
import numpy as np
import os
import traceback

from langchain_core.documents import Document
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from .twelvelabs_embedding import TwelveLabsEmbeddings


class FAISS_INDEX:
    def __init__(self, embedding_length=1024, k=5):
        self.embeddings_function = TwelveLabsEmbeddings()
        self.embedding_length = embedding_length
        self.faiss_index = faiss.IndexFlatL2(embedding_length)
        self.index_to_docstore_id = {}
        self.docstore = InMemoryDocstore()
        self.vector_store = FAISS(
           index=self.faiss_index,
           embedding_function=self.embeddings_function,
           docstore=self.docstore,
           index_to_docstore_id=self.index_to_docstore_id
        )
        self.k_results = k


    def format_video(self, start_time: int, end_time:int, video_name:str, chunk_num:int) -> Document:
        return Document(
            page_content=f'Audio segement {chunk_num}',
            metadata={
                "type": "video",
                "document_name": video_name,
                "start_time": start_time,
                "end_time": end_time
            }
        )
    
    def get_video_name(self, file_path:str): 
        return file_path.split('/')[-1]

    def add_video_chunks_to_index(self, segements: list[twelvelabs.models.embed.SegmentEmbedding], file_path:str):
        try: 
            print(segements)
            for i in range(len(segements)):
                embedding_object = segements[i]
                start = embedding_object.start_offset_sec
                end = embedding_object.end_offset_sec
                embeddings = embedding_object.embeddings_float
                doc_name = self.get_video_name(file_path=file_path)

                document = self.format_video(start, end, doc_name, i)
                self.faiss_index.add(np.array([embeddings], dtype=np.float32))
    
                doc_id = f'audio_segement_{i}'
                self.docstore._dict[doc_id] = document
                self.index_to_docstore_id[self.faiss_index.ntotal - 1] = doc_id
            print(f'Sucessfully added {len(segements)} audio segements to index')
        except Exception as e: 
            print('Adding chunks to index failed')
            traceback.print_exc()
            return {
                "status": 500,
                "error": e
            }
            
    def add_text_chunks_to_index(self, chunks:list[dict[str]], file_path: str):
        c_name = self.get_video_name(file_path=file_path)
        ids = [f'{c_name}_chunk_{i}' for i in range(len(chunks))]
        print("1")
        document_chunks = [Document(**chunk) for chunk in chunks]
        print("2")
        self.vector_store.add_documents(documents=document_chunks, ids=ids)
        print("3")
        print(f'Sucessfully added {len(chunks)} text chunks to index')
    
    def search(self, query:str, doc_name:str, most_similar:bool=False):
        results = self.vector_store.similarity_search(
            query=query,
            k=self.k_results,
            filter={"document_name": doc_name},
        )

        if most_similar:
            results_sorted = sorted(results, reverse=True)
            return results_sorted[0]
        
        return results

if __name__ == '__main__':
    # use case 

    #### videos ######
    if __name__ == "__main__":
        import requests

        api_key = "tlk_2AEMGCH2V8PG6W2YNRK9A30KDFXS"
        url = "https://api.twelvelabs.io/v1.3/engines"
        headers = {"x-api-key": api_key}

        response = requests.get(url, headers=headers)
        engines = response.json()

        for engine in engines:
            print(f"Name: {engine['name']}, ID: {engine['id']}, Type: {engine['type']}")

    #### text ####
    # text_chunker = NoteClusterer()
    # test_index = FAISS_INDEX()
    # file_path = 'backend/services/sample_pdf.pdf'
    # chunks = text_chunker.process_pdf(file_path=file_path)

    # doc_name = text_chunker.get_doc_name(file_path=file_path)
    # test_index.add_text_chunks_to_index(chunks=chunks)
    # print(test_index.search(query='what awards are mentioned'), doc_name)







