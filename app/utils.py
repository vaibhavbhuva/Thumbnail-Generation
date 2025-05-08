import os
from typing import Union
from urllib.parse import urlparse

ASSET_PREFIX = "/assets/public/"

MIME_TO_EXTENSION = {
    "image/png": "png",
    "image/jpeg": "jpg"
}

_FORMAT_TO_MIME_TYPE = {
    "png": "image/png",
    "jpeg": "image/jpeg",
    "jpg": "image/jpeg"
}

def format_storage_url(image_url: str, asset_prefix = ASSET_PREFIX) -> str:
    urlparts = urlparse(image_url)
    path_parts = urlparts.path.split("/")
    new_url = "https" + "://" + urlparts.netloc + \
        asset_prefix + "/".join(path_parts[2:])
    return new_url

def get_file_extension(file_path: str):
  default_ext  = "jpg"
  try:
    parsed_url = urlparse(file_path)
    path = parsed_url.path
    if path:
      _, ext = os.path.splitext(path)
      return ext.lower()
    else:
      return default_ext
  except Exception as e:
    print(f"get_file_extension :: Error parsing URL: {e}")
    return default_ext

def get_file_mimetype(file_path):
  extension = get_file_extension(file_path)
  return _FORMAT_TO_MIME_TYPE.get(extension, 'image/jpeg')

def get_extension_from_mimetype(mime_type) -> Union[str, None]:
    # Use a dictionary to map mimetypes to extensions
    return MIME_TO_EXTENSION.get(mime_type, "png")
