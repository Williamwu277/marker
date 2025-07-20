import os 
import io
import base64
import random
import string
from datetime import datetime
from google.oauth2 import service_account
from google.cloud import vision 
from pdf2image import convert_from_bytes, convert_from_path
from dotenv import load_dotenv
from PIL import Image
from .gemini_client import GeminiClient

load_dotenv(override=True)


class Parser:

    def __init__(self):

        credentials = service_account.Credentials.from_service_account_file(
            os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        )
        self.client = vision.ImageAnnotatorClient(credentials=credentials)
        self.gClient = GeminiClient()
        
        '''
        self.data = {
            "id": {
                "file_name": "name",
                "id": "random_id",
                "file_type": "video" or "pdf" or "png",
                "size": "size_in_bytes",
                "uploaded_at": "date_uploaded",
                "pages": [
                    {
                        "image": "base64_encoded_image",
                        "pages": {
                            "text_blocks": [
                                {
                                    "bounding_box": [(x, y), (x, y), (x, y), (x, y)],
                                    "text": "text"
                                }
                            ],
                            "dimensions": (width, height)
                        }
                    }
                ]
            }
        }
        '''
        self.data = {}
    
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
    def upload_png(self, png_bytes, file_name):
        images = [Image.open(io.BytesIO(png_bytes))]
        return self.extract_text(images, file_name, len(png_bytes))
    
    '''
    Given a pdf name and its form in bytes, upload the pdf to the database and parse the text
    Returns the generated ID
    '''
    def upload_pdf(self, pdf_bytes, pdf_name):
        images = convert_from_bytes(pdf_bytes, dpi=300)
        if len(images) > 5:
            raise ValueError("PDF must have less than 5 pages")
        
        return self.extract_text(images, pdf_name, len(pdf_bytes))
    
    '''
    Given a list of images, extract the text from the images and store it
    Returns the generated ID
    '''
    def extract_text(self, images, file_name, file_size):
        # Generate a unique ID for this PDF
        file_id = self.generate_random_id()
        
        # Initialize the PDF entry
        self.data[file_id] = {
            "file_name": file_name,
            "id": file_id,
            "file_type": "pdf" if file_name.endswith('.pdf') else "png",
            "size": file_size,
            "uploaded_at": datetime.now().isoformat(),
            "pages": []
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
                "pages": {
                    "dimensions": (width, height),
                    "text_blocks": []
                }
            })
            for block_num, block in enumerate(filtered_blocks, start=1):

                # print data for debugging
                print(f"Block {block_num}:")
                print(f" Bounding box: {block['verticies']}")
                print(f" Text: {block['text']}\n")

                self.data[file_id]["pages"][-1]["pages"]["text_blocks"].append({
                    "bounding_box": block["verticies"],
                    "text": block["text"]
                })
        
        return file_id
    
    def upload_test(self, file_path, file_name):
        images = convert_from_path(file_path, dpi=300)[:1]
        if len(images) > 5:
            raise ValueError("PDF must have less than 5 pages")
        
        return self.extract_text(images, file_name)
