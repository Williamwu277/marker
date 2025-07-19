from  twelvelabs import TwelveLabs
from typing import List
import os 
import time

class Embedder:
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
    
    def return_status(self):
        return self.embedding_object.status
    
    def update_status(self):
        if self.embedding_object: 
            while self.return_status() != 'ready':
                print(f'processing...')
                time.sleep(5)
                self.embedding_object = self.client.embed.task.retrieve(self.embedding_object.id)


if __name__ == "__main__": 
    # use case 
    embedder = Embedder()
    embedder.add_video('backend/utils/test_video/video3523442589.mp4')
    
    embedder.update_status()
    print(f'embedded video successfully.')
    embedder.embedding_object = embedder.client.embed.task.retrieve(embedder.embedding_object.id)
    
    embeddings = embedder.retrieve_embeddings(["audio"]) # can also add visual_text as an option 
    print(embeddings)


    
    
     
        








