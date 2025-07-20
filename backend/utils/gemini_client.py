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

    def generate_notes(self, context: str) -> str:
        # Generate initial notes with Gemini
        prompt_template = self.prompts['gemini']['notes']['prompt']
        contents = prompt_template.format(context=context)
        initial_response = self.generate_content(contents)
        
        # Validate and clean XML with OpenAI
        validated_xml = self.validate_xml(initial_response, "notes")
        return validated_xml
    
    def generate_practice_questions(self, context: str) -> str:
        prompt_template = self.prompts['gemini']['practice_questions']['prompt']
        contents = prompt_template.format(context=context)
        initial_response = self.generate_content(contents)
        # Validate and clean XML with OpenAI
        validated_xml = self.validate_xml(initial_response, "questions") 
        return validated_xml
    
    def filterQuestions(self, blocks: list[dict]) -> list[dict]:
        block_string = "\n".join([block["text"].replace("\n", " ") for block in blocks])
        prompt = f'''
        You are a helpful assistant that filters through a list of blocks of text and returns
        TRUE for the blocks that are most likely to be homework/test/assignment questions and FALSE otherwise.
        The input is a list of blocks of text, one being on each line. The output for EACH line is either TRUE 
        or FALSE depending on whether or not the block is a homework/test/assignment question.
        Do NOT output anything irrelevant.

        Example input:
        Calculate the area of the triangle with sides 3, 4, and 5.
        McDonalds is a fast food restaurant that sells big macs.
        Example output:
        TRUE
        FALSE

        Input:
        {block_string}
        Output:
        '''
        preliminary_response = self.generate_content(prompt)
        print("GEMINI RESPONSE:\n", preliminary_response, sep="")
        response = preliminary_response.split('\n')
        filtered_blocks = []
        for i in range(len(blocks)):
            if i >= len(response) or response[i] != "FALSE":
                filtered_blocks.append(blocks[i])
        print(*filtered_blocks)
        return filtered_blocks
    
    def format_extracted_text(self, raw_text: str) -> str:
        """
        Format extracted text blocks into a coherent educational summary.
        Args:
            text_blocks: List of dicts with {'text': str, 'bounding_box': list} from parser
        Returns:
            str: Formatted text summary suitable for worksheet/notes generation
        """
        print("Formatting extracted text with Gemini...")
        
        formatting_prompt = """
        Format this extracted text into clear, structured educational content.
        Follow these guidelines:

        1. Clean and organize the content:
        - Remove irrelevant headers, footers, page numbers
        - Fix any OCR errors or formatting issues
        - Ensure proper paragraph breaks
        - Preserve mathematical notation and symbols

        2. Structure the content:
        - Organize into logical sections
        - Highlight key concepts and definitions
        - Preserve important examples
        - Maintain natural flow between ideas

        3. Format rules:
        - Use complete sentences
        - Keep paragraph structure
        - Preserve technical terminology
        - Maintain academic tone

        Original text:
        {text}

        Return only the formatted content, no additional markup or instructions.
        """

        try:
            formatted_content = self.generate_content({
                "contents": formatting_prompt.format(text=raw_text)
            })
            return formatted_content.strip()
        except Exception as e:
            print(f"Text formatting failed: {e}")
            return raw_text  # Return original text if formatting fails

