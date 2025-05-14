import os
import math
import json
from pathlib import Path
import urllib.parse
import requests
import vertexai
import matplotlib.pyplot as plt
from typing import Any, Dict, List, Tuple
from dotenv import load_dotenv
from ...logger import logger
from ...utils import get_extension_from_mimetype, format_storage_url, MIME_TO_EXTENSION

from vertexai.generative_models import GenerativeModel, Part, Image , SafetySetting, GenerationConfig
from vertexai.preview.vision_models import ImageGenerationResponse, ImageGenerationModel
from ...libs.storage import GCPStorage
from ... import config

load_dotenv()

KB_API_HOST = os.environ["KB_API_HOST"]

# GCP Storage
storage = GCPStorage()
STORAGE_THUMBNAIL_FOLDER=os.environ["STORAGE_THUMBNAIL_FOLDER"]
STORAGE_PROXY_PATH=os.environ["STORAGE_PROXY_PATH"]

#GCP GEMINI VERTEX AI
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.environ["GCP_GEMINI_CREDENTIALS"]
vertexai.init(project=os.environ["GCP_GEMINI_PROJECT_ID"])

GEMINI_MODEL_PRO = os.environ["GEMINI_MODEL_PRO"]
VISION_MODEL = os.environ["VISION_MODEL"]
NUMBER_OF_IMAGES = os.environ["NUMBER_OF_IMAGES"]
DEFAULT_PROMPT=config.DEFAULT_PROMPT
# DEFAULT_PROMPT="What is in this image?" #
NEGATIVE_PROMPT = config.NEGATIVE_PROMPT
PERSON_GENERATION=config.PERSON_GENERATION
SAFETY_FILTER_LEVEL=config.SAFETY_FILTER_LEVEL
DEFAULT_ASPECT_RATIO = config.DEFAULT_ASPECT_RATIO
GUIDANCE_SCALE = config.GUIDANCE_SCALE
SEED = config.SEED


def fetch_content_details(content_id: str) -> dict:
    """Fetches the details of a content.

    Args:
        content_id (str): The ID of the content.

    Returns:
        dict: The content details.

    Raises:
        Exception: If there's an error fetching the content details.
    """

    url = f"{KB_API_HOST}/api/content/v1/read/{content_id}?mode=edit"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    logger.debug(f"course details :: {data}")
    return data


def format_thumbnail_url(content_details) -> str:
    """Formats the URL of the thumbnail image.

    Args:
        content_details (dict): The content details.

    Returns:
        str: The URL of the thumbnail image.
    """

    poster_img = content_details["result"]["content"]["posterImage"]
    image_url = format_storage_url(poster_img)
    logger.debug(f"Formatted storage thumbnail URL :: {image_url}")
    return image_url


def download_thumbnail(thumbnail_url: str) -> bytes:
    """Downloads the thumbnail image from the given URL.

    Args:
        thumbnail_url (str): The URL of the thumbnail image.

    Returns:
        bytes: The thumbnail image data.

    Raises:
        Exception: If there's an error downloading the thumbnail.
    """

    response = requests.get(thumbnail_url, stream=True)
    response.raise_for_status()
    image_type = response.headers["Content-Type"]
    logger.info(f"Thumbnail  content type :: {image_type}")
    # Check for image type, currently only PNG or JPEG format are supported
    if image_type not in MIME_TO_EXTENSION:
        raise ValueError(f"Image can only be in the following formats: {', '.join(MIME_TO_EXTENSION.keys())}")

    # Read the image data as bytes
    image_bytes = b''.join(response.iter_content(chunk_size=1024))
    return image_bytes


def download_content_thumbnail(content_id: str) -> tuple[str, bytes]:
    """Downloads the thumbnail for a given content ID.

    Args:
        content_id (str): The ID of the content.

    Returns:
        bytes: The thumbnail image data.

    Raises:
        Exception: If there's an error fetching the content details or thumbnail.
    """

    content_details = fetch_content_details(content_id)
    thumbnail_url = format_thumbnail_url(content_details)
    thumbnail_data = download_thumbnail(thumbnail_url)
    return thumbnail_url, thumbnail_data

def detect_logos(image_data: bytes) -> str:
    system_instruction = """You are a image data analyst with expertise in commercial logos. Please do not hallucinate. You can just output nothing if there are no positive findings."""
    model = GenerativeModel(
        GEMINI_MODEL_PRO,
        system_instruction=[system_instruction]
    )
    text_part = Part.from_text("""Identify and detect logos within an image, providing information about the logo\'s name, position, and confidence score.

        # Steps:
        1. **Image Analysis**: Load and preprocess the input image for logo detection, ensuring appropriate scaling and color adjustment.
        2. **Logo Detection**: Use a logo detection model or algorithm to identify potential logos within the image.
        3. **Localization and Classification**: Determine the position (bounding box) of each detected logo, classify it to identify its name, and calculate the detection confidence score.
        4. **Compile Results**: Gather the results, including logo name, position, and confidence score.


        # Notes
        - Ensure that the provided confidence score reflects the accuracy of the detection result.
        - Consider using pre-trained neural networks for more accurate logo detection and recognition.
        - Handle images of varying resolutions and formats for robust detection capabilities.

    """)
    image_part = Part.from_image(Image.from_bytes(image_data))
    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 1,
        "top_p": 0.95,
        "response_mime_type": "application/json",
        "response_schema": {
            "type_":"ARRAY",
            "items": {
                "type_":"OBJECT",
                "properties": {
                    "logo_name": {
                        "type_":"STRING"
                    },
                    "position":{
                        "type_":"OBJECT",
                        "properties":{
                        "x":{
                            "type_":"NUMBER"
                        },
                        "y":{
                            "type_":"NUMBER"
                        },
                        "width":{
                            "type_":"NUMBER"
                        },
                        "height":{
                            "type_":"NUMBER"
                        }
                        }
                    },
                    "confidence_score":{
                        "type_":"NUMBER"
                    }
                }
            }
        }
    }
    # safety_settings = [
    #     SafetySetting(
    #         category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
    #         threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE
    #     ),
    #     SafetySetting(
    #         category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
    #         threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE
    #     ),
    #     SafetySetting(
    #         category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
    #         threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE
    #     ),
    #     SafetySetting(
    #         category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
    #         threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE
    #     ),
    # ]
    response = model.generate_content(
        [image_part, text_part],
        generation_config=generation_config,
        # safety_settings=safety_settings,
        # stream=True,
    )
    logger.info(f"Logo Detection :: {response.text}")
    return json.loads(response.text)


def generate_content(image_data: bytes) -> str:
    gemini = GenerativeModel(GEMINI_MODEL_PRO)
    text_part = Part.from_text(DEFAULT_PROMPT)
    image_part = Part.from_image(Image.from_bytes(image_data))
    generation_config = GenerationConfig(
        # temperature=1,
        # top_p=0.95,
        # top_k=40,
        # candidate_count=1,
        max_output_tokens=512
    )
    # safety_settings = [
    #     SafetySetting(
    #         category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
    #         threshold=SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    #     ),
    #     SafetySetting(
    #         category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
    #         threshold=SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    #     ),
    #     SafetySetting(
    #         category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
    #         threshold=SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    #     ),
    #     SafetySetting(
    #         category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
    #         threshold=SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    #     ),
    # ]
    response = gemini.generate_content(
        contents = [image_part, text_part], 
        generation_config=generation_config,
        # safety_settings=safety_settings
    )
    logger.info(f"Generated content :: {response.text}")
    return response.text

def generate_image(image_prompt: str) -> ImageGenerationResponse:
    image_model = ImageGenerationModel.from_pretrained(VISION_MODEL)
    image_model.upscale_image
    images = image_model.generate_images(
        prompt=image_prompt,
        number_of_images=NUMBER_OF_IMAGES,
        aspect_ratio=DEFAULT_ASPECT_RATIO,
        safety_filter_level=SAFETY_FILTER_LEVEL,
        person_generation=PERSON_GENERATION,
        negative_prompt=NEGATIVE_PROMPT
    )
    return images

def generate_image_variations(content_id: str) -> Tuple[Dict[str, Any], List[str]]:
    image_url, image_data = download_content_thumbnail(content_id)
    logo_detection = {
        "found": False,
        "warning" : None
    }
    logo_results = detect_logos(image_data)
    if logo_results:
        logo_detection["found"] = True
        logo_detection["warning"] = "This image contains a logo. AI may not accurately generate changes to logos. This feature is currently in beta testing."
    image_prompt = generate_content(image_data)
    images = generate_image(image_prompt)
    original_file_name = Path(image_url).stem
    image_urls = []
    for index, image in enumerate(images):       
        extension = get_extension_from_mimetype(image._mime_type)
        filename = f"{original_file_name}_{index}.{extension}"
        filepath = os.path.join(STORAGE_THUMBNAIL_FOLDER, content_id, filename)
        logger.info(f"Filename :: {filepath}")
        storage.write_file(filepath, image._image_bytes, image._mime_type)
        # image_urls.append(storage.public_url(filepath))
        public_url = urllib.parse.urljoin(KB_API_HOST, os.path.join(STORAGE_PROXY_PATH, content_id, filename))
        image_urls.append(public_url)
    return logo_detection, image_urls