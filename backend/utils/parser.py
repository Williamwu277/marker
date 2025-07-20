import os 
import io
import base64
import random
import string
import tempfile
from datetime import datetime
from google.oauth2 import service_account
from google.cloud import vision 
from pdf2image import convert_from_bytes, convert_from_path
from dotenv import load_dotenv
from PIL import Image
from .gemini_client import GeminiClient
from backend.services.embedding.faiss_langchain_indexing import FAISS_INDEX
from langchain_core.documents import Document

load_dotenv(override=True)

class Parser:
    def __init__(self, gClient):

        credentials = service_account.Credentials.from_service_account_file(
            os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        )
        self.client = vision.ImageAnnotatorClient(credentials=credentials)
        self.gClient = gClient
        
        '''
        self.data = {
            "id": {
                "file_name": "name",
                "id": "random_id",
                "file_type": "video" or "pdf" or "png",
                "size": "size_in_bytes",
                "uploaded_at": "date_uploaded",
                "temp_path": "path_to_temp_file",  # Only for pdfs and videos
                "text_summary": "full_text" or "video_summary", 
                "file_usage": "notes" or "worksheet" or "video",
                "video_bytes"(?): "video_bytes",
                "pages"(?): [
                "pages": [
                    {
                        "image": "base64_encoded_image",
                        "dimensions": (width, height),
                        "text_blocks": [
                            {
                                "bounding_box": [(x, y), (x, y), (x, y), (x, y)],
                                "text": "text"
                            }
                        ],
                    }
                ]
            }
        }
        '''
        self.data = {}
        self.indexer = FAISS_INDEX()
    
    def generate_random_id(self):
        id = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        while id in self.data:
            id = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        return id
    
    '''
    Given an id, return the parsed data for that file
    '''
    def get_file(self, id):
        if id not in self.data:
            raise ValueError(f"File with ID {id} not found in storage")
        return self.data[id]

    '''
    Returns a list of all files in the database
    '''
    def get_all_files(self):
        return list(self.data.values())
    
    '''
    Given a png file in bytes, upload the file to the database and parse the text
    Returns the generated ID
    '''
    def upload_png(self, png_bytes, file_name, file_usage):
        images = [Image.open(io.BytesIO(png_bytes))]
        return self.extract_text(images, file_name, len(png_bytes), file_usage)
    
    '''
    Given a pdf name and its form in bytes, upload the pdf to the database and parse the text
    Returns the generated ID
    '''
    def upload_pdf(self, pdf_bytes, pdf_name, file_usage):
        temp_pdf_path = self.save_temp_pdf(pdf_bytes)

        images = convert_from_bytes(pdf_bytes, dpi=300)
        if len(images) > 5:
            raise ValueError("PDF must have less than 5 pages")
        
        
        file_id = self.extract_text(images, pdf_name, len(pdf_bytes), file_usage)
        self.data[file_id]["temp_path"] = temp_pdf_path

        return file_id
    
    def upload_video(self, video_bytes, file_name, file_usage):
        # Save to temp file
        temp_video_path = self.save_temp_video(video_bytes)

        # Generate unique ID
        file_id = self.generate_random_id()

        # Store metadata
        self.data[file_id] = {
            "file_name": file_name,
            "id": file_id,
            "file_type": "video",
            "size": len(video_bytes),
            "uploaded_at": datetime.now().isoformat(),
            "temp_path": temp_video_path,
            "pages": [],
            "file_usage": file_usage,
            "video_bytes": video_bytes
        }

        return file_id
    
    '''
    Given a list of images, extract the text from the images and store it
    Returns the generated ID
    '''
    def extract_text(self, images, file_name, file_size, file_usage):
        # Generate a unique ID for this PDF
        file_id = self.generate_random_id()
        
        # Initialize the PDF entry
        self.data[file_id] = {
            "file_name": file_name,
            "id": file_id,
            "file_type": "pdf" if file_name.endswith('.pdf') else "png",
            "size": file_size,
            "uploaded_at": datetime.now().isoformat(),
            "pages": [],
            "file_usage": file_usage,
            "video_bytes": None
        }
        
        # for each page
        for i, image in enumerate(images):

            # save the image to a buffer
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr_value = img_byte_arr.getvalue()
            img_byte_arr.seek(0)

            # convert to PIL image to get dimensions
            pil_image = Image.open(io.BytesIO(img_byte_arr_value))
            width, height = pil_image.size

            # extract the text
            gvision_image = vision.Image(content=img_byte_arr_value)
            response = self.client.document_text_detection(image=gvision_image)
            results = response.full_text_annotation

            # prepare the blocks for gemini to filter
            blocks = []
            for block in results.pages[0].blocks:
                # vertices
                vertices = [(v.x, v.y) for v in block.bounding_box.vertices]
                # text
                block_text = ""
                for paragraph in block.paragraphs:
                    for word in paragraph.words:
                        word_text = ''.join([symbol.text for symbol in word.symbols])
                        block_text += word_text + " "
                block_text = block_text.strip()
                blocks.append({
                    "verticies": vertices,
                    "text": block_text
                })
            
            # allow gemini to filter the blocks for questions
            filtered_blocks = self.gClient.filterQuestions(blocks)

            # for each block, add it to the data
            print(f"\n--- Page {i} ---")
            print(f"Dimensions: {width}x{height}")
            self.data[file_id]["pages"].append({
                "image": base64.b64encode(img_byte_arr.getvalue()).decode('utf-8'),
                "dimensions": (width, height),
                "text_blocks": []
            })
            for block_num, block in enumerate(filtered_blocks, start=1):

                # print data for debugging
                print(f"Block {block_num}:")
                print(f" Bounding box: {block['verticies']}")
                print(f" Text: {block['text']}\n")

                self.data[file_id]["pages"][-1]["text_blocks"].append({
                    "bounding_box": block["verticies"],
                    "text": block["text"]
                })
        
        return file_id
    
    def upload_test(self, file_path, file_name):
        images = convert_from_path(file_path, dpi=300)[:1]
        if len(images) > 5:
            raise ValueError("PDF must have less than 5 pages")
        
        return self.extract_text(images, file_name)

    def save_temp_pdf(self, pdf_bytes):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_file.write(pdf_bytes)
        temp_file.flush()
        temp_path = temp_file.name
        temp_file.close()
        return temp_path
    
    def save_temp_video(self, video_bytes):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        temp_file.write(video_bytes)
        temp_file.flush()
        temp_path = temp_file.name
        temp_file.close()
        return temp_path
    
    def find_bounding_box(self, filtered_name, similar_result: Document):
        query = similar_result['page_content']
        return self.indexer.search(query=query, doc_name=filtered_name, most_similar=True)['metadata']['bounding_box']

    def create_blocked_embeddings(self, file_blocks:list[dict], filtered_name):
        """
        file name should be a filtered name to sift through the documents only with a bounding box
        """
        try: 
            chunks = []
            for block in file_blocks:
                text = block.get('text_blocks')['text']
                bounding_box = block.get('text_blocks')['bounding_box']
                file_name = block.get('file_name')

                chunk = {
                    "page_content": text,
                    "metadata": {
                        "filtered_name": filtered_name,
                        "bounding_box": bounding_box
                    }
                }

                chunks.append(chunk)
            
            self.indexer.add_text_chunks_to_index(chunks=chunks, file_path=file_name)
        except Exception as e:
            return e


# use case for embeddings 
# 1. create the embeddings for the blocked chunks 
# 2. find the bounidng box -> creates a semantic search between the texts, returns the bounding box 




