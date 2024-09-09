from typing import Union
from urllib.parse import urlparse

ASSET_PREFIX = "/assets/public/"
MIME_TO_EXTENSION = {
    "image/png": "png",
    "image/jpeg": "jpg"
}

def format_storage_url(image_url: str, asset_prefix = ASSET_PREFIX) -> str:
    urlparts = urlparse(image_url)
    path_parts = urlparts.path.split("/")
    new_url = "https" + "://" + urlparts.netloc + \
        asset_prefix + "/".join(path_parts[2:])
    return new_url

def get_extension_from_mimetype(mime_type) -> Union[str, None]:
    # Use a dictionary to map mimetypes to extensions
    return MIME_TO_EXTENSION.get(mime_type, "png")
