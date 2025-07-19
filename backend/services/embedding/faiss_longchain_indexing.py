import faiss 
import twelvelabs
import numpy as np

from langchain_core.documents import Document
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from twelvelabs_embedding import TwelveLabsEmbeddings
from note_upload import NoteClusterer


class FAISS_INDEX:
    def __init__(self, embedding_length=1024, k=5):
        self.embeddings_function = TwelveLabsEmbeddings(model='Marengo-retrieval-2.7')
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
                "video_name": video_name,
                "start_time": start_time,
                "end_time": end_time
            }
        )

    def add_video_chunks_to_index(self, segements: list[twelvelabs.models.embed.SegmentEmbedding], video:str):
        try: 
            for i in range(len(segements)):
                embedding_object = segements[i]
                start = embedding_object.start_offset_sec
                end = embedding_object.end_offset_sec
                embeddings = embedding_object.embeddings_float

                document = self.format_video(start, end, video, i)
                self.faiss_index.add(np.array([embeddings], dtype=np.float32))
    
                doc_id = f'audio_segement_{i}'
                self.docstore._dict[doc_id] = document
                self.index_to_docstore_id[self.faiss_index.ntotal - 1] = doc_id
            print(f'Sucessfully added {len(segements)} audio segements to index')
        except Exception as e: 
            print('Adding chunks to index failed')
            return {
                "status": 500,
                "error": e
            }
            

    def add_text_chunks_to_index(self, chunks:list[dict[str]]):
        c_name = chunks[0]['metadata']['document_name']
        ids = [f'{c_name}_chunk_{i}' for i in range(len(chunks))]
        document_chunks = [Document(**chunk) for chunk in chunks]
        self.vector_store.add_documents(documents=document_chunks, ids=ids)
    
    def search(self, query:str, filter:dict={}):
        results = self.vector_store.similarity_search(
            query=query,
            k=self.k_results,
            filter=filter,
        )
        return results 
    

if __name__ == '__main__':
    # use case 

    #### videos ######
    # test_index = FAISS_INDEX()
    # embedder = TwelveLabsEmbeddings()
    # video_path = 'backend/services/embedding/test_video/video3523442589.mp4'
    # chunk_embeddings = embedder.embed_video(video=video_path)
    # test_index.add_video_chunks_to_index(chunk_embeddings, video_path)
    # print(test_index.search(query='what design elements are in this'))

    #### text ####
    text_chunker = NoteClusterer()
    test_index = FAISS_INDEX()
    chunks = text_chunker.process_pdf(file_path='backend/services/sample_pdf.pdf')
    test_index.add_text_chunks_to_index(chunks=chunks)
    # print(test_index.search(query='what awards are mentioned'))







