import os
import math
import uuid
from pathlib import Path
import requests
import vertexai
import matplotlib.pyplot as plt
from typing import List
from dotenv import load_dotenv
from ..logger import logger
from ..utils import get_extension_from_mimetype, format_storage_url, MIME_TO_EXTENSION

from vertexai.generative_models import GenerativeModel, Part, Image
from vertexai.preview.vision_models import ImageGenerationResponse, ImageGenerationModel
from ..libs.storage import GCPStorage

load_dotenv()

KB_API_HOST = os.environ["KB_API_HOST"]
storage = GCPStorage()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.environ["GCP_GEMINI_CREDENTIALS"]
vertexai.init(project=os.environ["GCP_GEMINI_PROJECT_ID"])
STORAGE_THUMBNAIL_FOLDER="thumbnail_images"
STORAGE_PROXY_PATH="/thumbnails/generate/"

# Default parameters for vertex AI - gemini
DEFAULT_PROMPT="You are an expert in writing prompts for image generation model and have immense knowledge of photography, based on given image and settings, generate a 150 words prompt adding supporting props to the image subject, but do NOT add too much information, keep it on the simpler side. Add 'a photo of' prefix to a prompt"
# DEFAULT_PROMPT="What is in this image?" #
NEGATIVE_PROMPT = """1. Avoid maps or geographical locations that promote stereotypes or favor certain regions
2. Avoid content that promotes or disparages any particular religion or religious belief.
3. Avoid content that reinforces gender stereotypes or biases.
"""
PERSON_GENERATION="allow_adult"
SAFETY_FILTER_LEVEL="block_some"
DEFAULT_ASPECT_RATIO = "4:3"
GEMINI_MODEL_PRO = os.environ["GEMINI_MODEL_PRO"]
VISION_MODEL = os.environ["VISION_MODEL"]
NUMBER_OF_IMAGES = 2
GUIDANCE_SCALE = 90
SEED = 915


def fetch_content_details(content_id: str) -> dict:
    """Fetches the details of a content.

    Args:
        content_id (str): The ID of the content.

    Returns:
        dict: The content details.

    Raises:
        Exception: If there's an error fetching the content details.
    """

    url = f"{KB_API_HOST}/api/content/v1/read/{content_id}"
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


def generate_content(image_data: bytes) -> str:
    gemini = GenerativeModel(GEMINI_MODEL_PRO)
    text_part = Part.from_text(DEFAULT_PROMPT)
    image_part = Part.from_image(Image.from_bytes(image_data))
    response = gemini.generate_content([image_part, text_part])
    logger.info(f"Generated content :: {response.text}")
    return response.text


def display_images_in_grid(images):
    """Displays the provided images in a grid format. 4 images per row.

    Args:
        images: A list of PIL Image objects representing the images to display.
    """

    # Determine the number of rows and columns for the grid layout.
    nrows = math.ceil(len(images) / 4)  # Display at most 4 images per row
    # Adjust columns based on the number of images
    ncols = min(len(images) + 1, 4)

    # Create a figure and axes for the grid layout.
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(12, 6))

    for i, ax in enumerate(axes.flat):
        if i < len(images):
            # Display the image in the current axis.
            ax.imshow(images[i]._pil_image)

            # Adjust the axis aspect ratio to maintain image proportions.
            ax.set_aspect("equal")

            # Disable axis ticks for a cleaner appearance.
            ax.set_xticks([])
            ax.set_yticks([])
        else:
            # Hide empty subplots to avoid displaying blank axes.
            ax.axis("off")

    # Adjust the layout to minimize whitespace between subplots.
    plt.tight_layout()

    # Display the figure with the arranged images.
    plt.show()


def generate_image(image_prompt: str) -> ImageGenerationResponse:

    # if not image_prompt:
    #     raise TypeError("image_prompt must not be empty")

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

def generate_image_variations(content_id: str) -> List[str]:
    image_url, image_data = download_content_thumbnail(content_id)
    image_prompt = generate_content(image_data)
    images = generate_image(image_prompt)
    original_file_name = Path(image_url).stem
    image_urls = []
    for image in images:       
        extension = get_extension_from_mimetype(image._mime_type)
        filename = f"{original_file_name}.{extension}"
        filepath = os.path.join(STORAGE_THUMBNAIL_FOLDER, content_id, filename)
        logger.info(f"Filename :: {filepath}")
        storage.write_file(filepath, image._image_bytes, image._mime_type)
        # image_urls.append(storage.public_url(filepath))
        public_url = KB_API_HOST + STORAGE_PROXY_PATH + content_id + "/" + filename
        image_urls.append(public_url)
    return image_urls
