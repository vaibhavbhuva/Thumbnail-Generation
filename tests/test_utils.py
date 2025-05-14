from unittest.mock import patch
import pytest
from urllib.parse import urlparse
from app.utils import (
    DEFAULT_EXTENSION,
    format_storage_url,
    get_file_extension,
    get_file_mimetype,
    get_extension_from_mimetype
)

# Test cases for format_storage_url
@pytest.mark.parametrize("input_url,expected_output", [
    (
        "https://example.com/storage/abc/image.jpg",
        "https://example.com/assets/public/abc/image.jpg"
    ),
    (
        "https://mydomain.com/media/uploads/img.png",
        "https://mydomain.com/assets/public/uploads/img.png"
    ),
])
def test_format_storage_url(input_url, expected_output):
    """Tests a standard URL with multiple path segments."""
    assert format_storage_url(input_url) == expected_output

def test_format_storage_url_custom_prefix():
    """Tests formatting with a custom asset prefix."""
    url = "http://example.com/some/path/image.jpg"
    custom_prefix = "/static/"
    expected = "https://example.com/static/path/image.jpg"
    assert format_storage_url(url, asset_prefix=custom_prefix) == expected


# Test cases for get_file_extension
@pytest.mark.parametrize("input_path,expected_ext", [
    ("https://example.com/path/to/image.JPG", "jpg"),  #getting extension from a URL with an uppercase extension
    ("https://example.com/image.png", "png"),
    ("https://example.com/image", "jpg"),  #Should return default on error
    ("", "jpg"),   #fallback
    ("/local/path/to/file.jpeg", "jpeg"),
])
def test_get_file_extension(input_path, expected_ext):
    """Tests getting extension from a URL."""
    assert get_file_extension(input_path) == expected_ext   

def test_get_file_extension_error_handling():
    # Simulate urlparse raising an exception
    with patch("app.utils.urlparse", side_effect=Exception("Simulated failure")):
        result = get_file_extension("https://example.com/image.png")
        assert result == DEFAULT_EXTENSION

# Test cases for get_file_mimetype
@pytest.mark.parametrize("input_path,expected_mime", [
    ("https://example.com/image.jpg", "image/jpeg"),
    ("https://example.com/image.png", "image/png"),
    ("https://example.com/image", "image/jpeg"), # Fallback
    ("", "image/jpeg"), #Should return default on error
])
def test_get_file_mimetype(input_path, expected_mime):
    """Tests getting mimetype for a file."""
    assert get_file_mimetype(input_path) == expected_mime

def test_get_file_mimetype_unsupported_extension():
    """Tests getting mimetype for an unsupported extension."""
    file_path = "http://example.com/document.gif"
    assert get_file_mimetype(file_path) == "image/jpeg" # Default mimetype


# Test cases for get_extension_from_mimetype
@pytest.mark.parametrize("input_mime,expected_ext", [
    ("image/png", "png"),
    ("image/jpeg", "jpg"),
    ("application/octet-stream", "png"),  #Should return default for unsupported mimetype     
    ("text/plain", "png"),  # fallback
])
def test_get_extension_from_mimetype(input_mime, expected_ext):
    """Tests getting extension for image/png mimetype."""
    assert get_extension_from_mimetype(input_mime) == expected_ext
