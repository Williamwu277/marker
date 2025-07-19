from  twelvelabs import TwelveLabs
from typing import List
import os 
import time

class TwelveLabsEmbeddings:
    def __init__(self, model='Marengo-retrieval-2.7'):
        self.model_name = model 
        self.api_key = os.environ.get('TWELVE_LABS_API')
        self.client = TwelveLabs(api_key=self.api_key)
        self.embedding_clip_length = 8
        self.embedding_object = None
    
    def add_video(self, video: str):
        try:
            self.embedding_object = self.client.embed.task.create(
                model_name=self.model_name,
                video_file=video,
                video_clip_length=self.embedding_clip_length
            )

            print(
            f"Created task: id={self.embedding_object.id} model_name={self.embedding_object.model_name} status={self.embedding_object.status}")
        except Exception as e:
            return {
                "status": 400,
                "error": e
            }
    
    def retrieve_embeddings(self, embedding_option: List[str]):
        if self.embedding_object:
            try:
                return self.embedding_object.retrieve(embedding_option=embedding_option).video_embedding.segments
            except Exception as e:
                return {
                    "status": 500,
                    "error": e
                }
    
    def return_status(self) -> str:
        return self.embedding_object.status
    
    def update_status(self):
        if self.embedding_object: 
            while self.return_status() != 'ready':
                print(f'processing...')
                time.sleep(5)
                self.embedding_object = self.client.embed.task.retrieve(self.embedding_object.id)
    
    def embed_video(self, video:str):
        """
            Embed a video based on file path 
        """
        try:
            self.add_video(video=video)
            self.update_status()
            print(f'embedded video successfully.')

            self.embedding_object = self.client.embed.task.retrieve(self.embedding_object.id)
            embeddings = embedder.retrieve_embeddings(["audio"])
            return embeddings
        except Exception as e:
            return {
                "status": 600,
                "error": e
            }
            
    def embed_query(self, query:str):
        """
        Embeds the query 
        """
        raise NotImplementedError
    
    def embed_documents(self, documents:List[str]):
        """
        Embeds the documents 
        """
        try:
            res = self.client.embed.create(model_name="Marengo-retrieval-2.7", text=text)
            print(f"Created text embedding: id={res.id} model_name={res.model_name} status={res.status}")
            return res
        except Exception as e:
            return {
                "status": 400,
                "error": e
            }


if __name__ == "__main__": 
    # use case 
    embedder = TwelveLabsEmbeddings()
    print(embedder.embed_video(video='backend/services/embedding/test_video/video3523442589.mp4'))
    

    
    
     
        








