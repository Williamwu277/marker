import os
import yaml
from dotenv import load_dotenv
from google import genai


class GeminiClient:
    def __init__(self, model="gemini-2.5-flash"):
        api_key = os.environ["GEMINI_API_KEY"]
        self.client = genai.Client(api_key=api_key)
        self.model = model
        
        # Load prompts from YAML file
        prompts_path = os.path.join(os.path.dirname(__file__), 'templates' , 'prompts.yaml')
        with open(prompts_path, 'r') as f:
            self.prompts = yaml.safe_load(f)

    def generate_content(self, contents): # API call to generate content
        print("Generating Content With Gemini...")
        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
        )
        return response.text
    
    
    def generate_practice_questions(self, topic, num_questions):
        prompt_template = self.prompts['gemini']['practice_questions']['prompt']
        contents = prompt_template.format(num_questions=num_questions, topic=topic)
        response = self.generate_content(contents)
        return response

    def generate_notes(self, topic):
        prompt_template = self.prompts['gemini']['notes']['prompt']
        contents = prompt_template.format(topic=topic)
        response = self.generate_content(contents)
        return response
    
    def analyze_written_work(self, text):
        prompt_template = self.prompts['gemini']['analyze_written_work']['prompt']
        contents = prompt_template.format(text=text)
        response = self.generate_content(contents)
        return response

    
load_dotenv()
gemini = GeminiClient()
print(gemini.generate_notes("python programming"))