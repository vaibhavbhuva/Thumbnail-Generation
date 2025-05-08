from PIL import Image
import base64
import io
import os
from dotenv import load_dotenv
from typing import Dict
import urllib.parse
import requests
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import openai
from ...utils import get_extension_from_mimetype

# Load environment variables from .env file
load_dotenv()
KB_API_HOST = os.environ["KB_API_HOST"]

from ...libs.storage import GCPStorage
storage = GCPStorage()

STORAGE_THUMBNAIL_FOLDER=os.environ["STORAGE_THUMBNAIL_FOLDER"]
STORAGE_PROXY_PATH=os.environ["STORAGE_PROXY_PATH"]

llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")
# Define prompt
prompt = ChatPromptTemplate.from_messages(
    [(
        "system",
        """
        Mission Karmayogi is a comprehensive program designed to transform the Indian civil service into a highly competent, citizen-centric, and effective force. 
        Its core objectives are to:

        - Foster a civil service rooted in Indian values and priorities.
        - Enhance public service delivery through effective and efficient governance.
        - Empower civil servants to excel in challenging environments.
        - Strengthen government-citizen interaction and promote ease of living and doing business.

        You are excellent at generating summary of a course hosted in mission Karmayogi web application.
        Below is the Course information:

        Course Name: {title}
        Course Description: {description}
        Course TOC:
          {toc}
        
        SUMMARY:
        """
    )]
)

# Define Image Generation Prompt
prompt_template = """
You are an expert Prompt Generator for Large Language Models.
Your goal is to generate a short prompt to generate an image based on the following description:

DESCRIPTION:
{text}

Here's an example of a great prompt:
Example 1: Generate an image of a computer chip, with the phrase 'Hello World' integrated into the circuitry design, symbolizing the intersection of technology and programming.
Example 2: In a fantastical setting, a highly detailed furry humanoid skunk with piercing eyes confidently poses in a medium shot,
wearing an animal hide jacket. The artist has masterfully rendered the character in digital art, capturing the intricate details
of fur and clothing texture.
Example 3: Sci-fi themed portrait featuring a holographic projection of the Microsoft logo bathed in neon lights. Vivid and striking color palette, dynamic angles, illuminated by futuristic lighting. 
Example 4:  A high-tech exhibition scene showcasing a 3D hologram of the Google logo, surrounded by interactive displays. Electrifying color contrasts, dynamic spatial arrangement, highlighted with LED strip lighting
Example 5: Travel guide book cover for "Hidden Gems of Europe", with the title in crisp text, overlaid on images of quaint European streets and landmarks 

Generated Prompt should include following instructions: 
- Please ensure that the image does not include any text or human imagery.
- Generate image without map of india.

GENERATE PROMPT"""


def get_course_details(course_id: str) -> Dict[str, any]:

    url = f"{KB_API_HOST}/api/course/v1/hierarchy/{course_id}?hierarchyType=detail"
    response = requests.get(url, headers={})
    
    try:
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        raise Exception("An error occurred while retrieving course details.")

def format_course_toc(data):
  """
  This function parses the input data (a dictionary) and returns the Course TOC
  as a formatted string.

  Args:
      data: A dictionary containing the course data.

  Returns:
      A string representing the Course TOC with indentation.
  """
  toc = ""
  if "children" in data:
    for child in data["children"]:
      # Check if child has a name
      if "name" in child:
        # Add indentation for child level
        toc += f"  - {child['name']}\n"
        # If child has children recursively call the function
        # if "children" in child:
        #   toc += format_course_toc(child)
  return toc

def generate_course_summary(course_id: str):
    course_details = get_course_details(course_id)
    formatted_toc = format_course_toc(course_details["result"]["content"])
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({
        "title": course_details["result"]["content"]["name"],
        "description": course_details["result"]["content"]["description"], 
        "toc": formatted_toc
      })
    return course_details["result"]["content"], result

def generate_image_prompt(summary: str):
    prompt = PromptTemplate.from_template(prompt_template)
    llmChatModel = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2
    )
    chain = prompt | llmChatModel | StrOutputParser()
    result = chain.invoke({"text": summary})
    return result

def generate_image(image_prompt: str):
    ############################
    # Generate a thumbnail image
    prompt = f"""
    Do not print any text on image, just use it AS-IS:
    {image_prompt}

    Guidelines:
    - Please ensure that the image does not include any text or human imagery.
    - Generate image without map of india.
    """
    response = openai.images.generate(
        prompt=prompt,
        model="dall-e-3",
        size="1024x1024",
        quality="standard",
        n=1,
        response_format="b64_json"
    )
    return response.data[0].b64_json

# Compress and convert image to JPEG
def compress_image(image_data):
    # Decode the base64 image data
    image_bytes = base64.b64decode(image_data)
    
    # Load the image into a PIL Image object
    image = Image.open(io.BytesIO(image_bytes))

    # Convert to JPEG and compress the image
    compressed_buffer = io.BytesIO()
    image.save(compressed_buffer, format="JPEG", quality=80)  # Adjust quality if needed
    compressed_image_data = compressed_buffer.getvalue()
    return compressed_image_data

def generate_public_url(content, image_data, mime_type = None):

    if mime_type is None:
       mime_type = "image/jpeg"

    compressed_image_data = compress_image(image_data)
    
    extension = get_extension_from_mimetype(mime_type)
    filename = f"{content["name"]}.{extension}"
    filepath = os.path.join(STORAGE_THUMBNAIL_FOLDER, content["identifier"], filename)
    storage.write_file(filepath, compressed_image_data, mime_type)
    # image_urls.append(storage.public_url(filepath))
    public_url = urllib.parse.urljoin(KB_API_HOST, os.path.join(STORAGE_PROXY_PATH, content["identifier"], filename))
    return public_url