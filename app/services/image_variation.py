import os
import math
import uuid
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

# Default parameters for vertex AI - gemini
NEGATIVE_PROMPT = "Country flag and map, Foreign people"
PERSON_GENERATION="allow_all"
SAFETY_FILTER_LEVEL="block_some"
DEFAULT_ASPECT_RATIO = "4:3"
GEMINI_MODEL_PRO = os.environ["GEMINI_MODEL_PRO"]
VISION_MODEL = os.environ["VISION_MODEL"]
NUMBER_OF_IMAGES = 4
GUIDANCE_SCALE = 90
SEED = 915

def download_content_thumbnail(content_id) -> bytes:
    url = f"{KB_API_HOST}/api/content/v1/read{content_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        logger.debug(f"course details :: {data}")
        appIcon = data["result"]["content"]["posterImage"]
        image_url = format_storage_url(appIcon)
        logger.debug(f"Formtted storage thumbnail URL :: {image_url}")
        try:
            resource_response = requests.get(image_url, stream=True)
            resource_response.raise_for_status()
            image_type = resource_response.headers["Content-Type"]
            
            # Check for image type, currently only PNG or JPEG format are supported
            if image_type not in MIME_TO_EXTENSION:
                raise ValueError(f"Image can only be in the following formats: {', '.join(MIME_TO_EXTENSION.keys())}")

            # Read the image data as bytes
            image_bytes = b''.join(
                resource_response.iter_content(chunk_size=1024))
            return image_bytes
        except requests.exceptions.RequestException as e:
            raise Exception("We encountered an error while retrieving the current thumbnail.")

    except requests.exceptions.RequestException as e:
        raise Exception("An error occurred while retrieving course details.")


def generate_content(image_data: bytes) -> str:
    gemini = GenerativeModel(GEMINI_MODEL_PRO)
    text_part = Part.from_text("What is in this image?")
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
    image_model = ImageGenerationModel.from_pretrained(VISION_MODEL)
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
    image_data = download_content_thumbnail(content_id)
    image_prompt = generate_content(image_data)
    images = generate_image(image_prompt)
    image_urls = []
    for image in images:
        extension = get_extension_from_mimetype(image._mime_type)
        filepath = f"{uuid.uuid4()}.{extension}"
        logger.info(f"Filename :: {filepath}")
        storage.write_file(filepath, image._image_bytes, image._mime_type)
        # image_urls.append(storage.public_url(filepath))
        image_urls.append(filepath)
    return image_urls
