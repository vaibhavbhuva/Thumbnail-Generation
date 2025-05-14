import os
from typing import Union
from urllib.parse import urlparse

# Constants
ASSET_PREFIX: str = "/assets/public/"

# Mappings
MIME_TO_EXTENSION: dict[str, str] = {
    "image/png": "png",
    "image/jpeg": "jpg"
}

EXTENSION_TO_MIME_TYPE: dict[str, str] = {
    "png": "image/png",
    "jpeg": "image/jpeg",
    "jpg": "image/jpeg"
}

# Default values
DEFAULT_EXTENSION: str = "jpg"
DEFAULT_MIME_TYPE: str = "image/jpeg"

def format_storage_url(image_url: str, asset_prefix = ASSET_PREFIX) -> str:
    urlparts = urlparse(image_url)
    path_parts = urlparts.path.split("/")
    new_url = "https" + "://" + urlparts.netloc + \
        asset_prefix + "/".join(path_parts[2:])
    return new_url

def get_file_extension(file_path: str):
  try:
    parsed_url = urlparse(file_path)
    path = parsed_url.path
    if path:
      _, ext = os.path.splitext(path)
      return ext.lower().lstrip(".") if ext else DEFAULT_EXTENSION
    else:
      return DEFAULT_EXTENSION
  except Exception as e:
    print(f"get_file_extension :: Error parsing URL: {e}")
    return DEFAULT_EXTENSION

def get_file_mimetype(file_path):
  extension = get_file_extension(file_path)
  return EXTENSION_TO_MIME_TYPE.get(extension, DEFAULT_MIME_TYPE)

def get_extension_from_mimetype(mime_type: str) -> Union[str, None]:
    # Use a dictionary to map mimetypes to extensions
    return MIME_TO_EXTENSION.get(mime_type.lower(), "png")
