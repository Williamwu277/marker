import os
import yaml
from dotenv import load_dotenv
from google import genai
from openai import OpenAI


class GeminiClient:
    def __init__(self, model="gemini-2.5-flash"):
        # Initialize Gemini
        api_key = os.environ["GEMINI_API_KEY"]
        self.client = genai.Client(api_key=api_key)
        self.model = model
        
        # Initialize OpenAI
        self.openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        
        # Load prompts from YAML file
        prompts_path = os.path.join(os.path.dirname(__file__), 'prompts.yaml')
        with open(prompts_path, 'r') as f:
            self.prompts = yaml.safe_load(f)

    def generate_content(self, contents): # API call to generate content
        print("Generating Content With Gemini...")
        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
        )
        return response.text

    def validate_xml(self, xml_content: str, type: str) -> str:
        """Validate and clean XML using OpenAI."""
        print("Validating XML with OpenAI...")
        try:
            # Get validation prompt from YAML config
            prompt_template = self.prompts['openai']['xml_verification'][type]
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": prompt_template},
                    {"role": "user", "content": xml_content}
                ],
                temperature=0.1  # Lower temperature for more consistent output
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI validation failed: {e}")
            return xml_content  # Return original if validation fails

    def generate_notes(self, topic: str, context: str) -> str:
        # Generate initial notes with Gemini
        prompt_template = self.prompts['gemini']['notes']['prompt']
        contents = prompt_template.format(topic=topic, context=context)
        initial_response = self.generate_content(contents)
        
        # Validate and clean XML with OpenAI
        validated_xml = self.validate_xml(initial_response, "notes")
        return validated_xml
    
    def generate_practice_questions(self, topic: str, context: str) -> str:
        prompt_template = self.prompts['gemini']['practice_questions']['prompt']
        contents = prompt_template.format(topic=topic, context=context)
        initial_response = self.generate_content(contents)
        # Validate and clean XML with OpenAI
        validated_xml = self.validate_xml(initial_response, "questions") 
        return validated_xml