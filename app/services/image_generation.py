from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel
import os
import json
from services.storage import upload_blob
import hashlib

with open('conf/config.json') as config_file:
    CONF = json.load(config_file)
#Initialize environment variable with google auth creds
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="app/config/vertex_key.json"

#setting project and location for image generation service account
PROJECT_ID = CONF['project_id_ai']
LOCATION = CONF['location']
#initialize vertexai with project id and server location
vertexai.init(project=PROJECT_ID, location=LOCATION)
#initialize vertexai image generation model
generation_model = ImageGenerationModel.from_pretrained(CONF['image_gen_model'])

# Initialize the language model for image generation
llm_image_generation = ChatOpenAI(model=CONF['llm_model'], temperature=0)
# Define the prompt template for image generation
image_prompt_template = """
    Generate a short prompt (must be length 1000 or less) to generate an image based on the following description:
    {text}
    Note: DO NOT PRINT/ADD ANY TEXT ON IMAGE.
"""

image_prompt = ChatPromptTemplate.from_template(image_prompt_template)

async def generate_image_prompt(final_summary):
    image_chain = image_prompt | llm_image_generation | StrOutputParser()
    image_prompt_result = await image_chain.ainvoke({"text": final_summary})
    return image_prompt_result

async def generate_image(image_prompt):
    # Generate a thumbnail image using DallEAPIWrapper
    image_url = DallEAPIWrapper(model="dall-e-3").run(f"""
    DO NOT print any text on image, just use it AS-IS:
    {image_prompt}

    Guidelines:
    ------------
      - Do not include any text.
      - Generate image without map of india.
    """)
    
    return image_url

async def generate_image_vertexai(image_prompt):
    image = generation_model.generate_images(
    prompt=image_prompt,
    number_of_images=1,
    aspect_ratio=CONF['image_aspect_ratio'],
    safety_filter_level="block_some",
    person_generation="allow_all",
    )
    image_name = str(hashlib.shake_128(b"my ascii string").hexdigest(4)) + '.jpg'
    image_url = upload_blob(CONF['thumb_storage_bucket'],image_name, image_name, CONF['project_id_storage'])
    return image_url