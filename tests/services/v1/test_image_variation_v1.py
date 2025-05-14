import json
from unittest.mock import MagicMock, patch
import requests
import pytest
from app.services.v1.image_variation import (detect_logos, download_content_thumbnail, download_thumbnail, fetch_content_details, format_thumbnail_url, generate_content)

def test_fetch_content_details_request_exception(mocker):
    """Tests handling of TypeError."""

    with pytest.raises(TypeError) as errInfo:
        fetch_content_details()

    assert "missing 1 required positional argument: 'content_id'" in str(errInfo)

def test_fetch_content_details_success(mocker):
    """Tests successful fetching of content details."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"result": {"content": {"posterImage": "some_image.jpg"}}}
    mock_get = mocker.patch("requests.get", return_value=mock_response)
    mock_logger_debug = mocker.patch("app.services.v1.image_variation.logger") # Adjust patch target

    content_id = "test_content_123"
    expected_url = f"https://portal.dev.karmayogibharat.net/api/content/v1/read/{content_id}?mode=edit"

    details = fetch_content_details(content_id)

    mock_get.assert_called_once_with(expected_url)
    mock_response.raise_for_status.assert_called_once()
    mock_response.json.assert_called_once()
    mock_logger_debug.debug.assert_called_once_with(f"course details :: {details}")
    assert details == {"result": {"content": {"posterImage": "some_image.jpg"}}}

def test_fetch_content_details_invalid_id(mocker):
    """
    Tests handling of an invalid content_id (e.g., empty string)
    in fetch_content_details.
    """
    # Mock a response with an error status code (e.g., 404 Not Found)
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Client Error: Not Found for url: ...")
    mock_get = mocker.patch("requests.get", return_value=mock_response)

    invalid_content_id = "" # Test with an empty string
    expected_url = f"https://portal.dev.karmayogibharat.net/api/content/v1/read/{invalid_content_id}?mode=edit"

    # Assert that calling the function with an invalid ID raises an HTTPError
    with pytest.raises(requests.exceptions.HTTPError) as excinfo:
        fetch_content_details(invalid_content_id)

    # Optionally, you can check the error message
    assert "404 Client Error" in str(excinfo.value)

    # Assert that requests.get was called with the expected URL
    mock_get.assert_called_once_with(expected_url)

    # Assert that raise_for_status was called
    mock_response.raise_for_status.assert_called_once()

    # Assert that json() was NOT called, as an exception was raised before it
    mock_response.json.assert_not_called()  


def test_format_thumbnail_url_success(mocker):
    """Tests successful formatting of thumbnail URL."""

    content_details = {"result": {"content": {"posterImage": "http://dev.portal.com/content/original_url.png"}}}
    expected_url = "https://dev.portal.com/assets/public/original_url.png"

    formatted_url = format_thumbnail_url(content_details)

    assert formatted_url == expected_url


def test_format_thumbnail_url_exception(mocker):
    """Tests handling of TypeError."""

    with pytest.raises(TypeError) as errInfo:
        format_thumbnail_url()

    assert "missing 1 required positional argument" in str(errInfo)

def test_format_thumbnail_url_missing_key():
    """Tests handling of missing posterImage key."""
    content_details = {"result": {"content": {}}}

    with pytest.raises(KeyError):
        format_thumbnail_url(content_details)


def test_download_thumbnail_success(mocker):
    """Tests successful downloading of thumbnail."""
    mock_response = MagicMock()
    mock_response.headers = {"Content-Type": "image/png"}
    mock_response.iter_content.return_value = [b"chunk1", b"chunk2"]
    mock_get = mocker.patch("requests.get", return_value=mock_response)

    thumbnail_url = "http://mock-url/image.png"
    expected_bytes = b"chunk1chunk2"

    image_data = download_thumbnail(thumbnail_url)

    mock_get.assert_called_once_with(thumbnail_url, stream=True)
    mock_response.raise_for_status.assert_called_once()
    assert image_data == expected_bytes


def test_download_thumbnail_unsupported_mime_type(mocker):
    """Tests handling of unsupported MIME type."""
    mock_response = MagicMock()
    mock_response.headers = {"Content-Type": "image/gif"}
    mock_get = mocker.patch("requests.get", return_value=mock_response)

    thumbnail_url = "http://mock-url/image.gif"

    with pytest.raises(ValueError) as excinfo:
        download_thumbnail(thumbnail_url)

    mock_get.assert_called_once_with(thumbnail_url, stream=True)
    mock_response.raise_for_status.assert_called_once()
    assert "Image can only be in the following formats: image/png, image/jpeg" in str(excinfo.value)

def test_download_thumbnail_exception(mocker):
    """Tests handling of TypeError."""

    with pytest.raises(TypeError) as errInfo:
        format_thumbnail_url()

    assert "missing 1 required positional argument" in str(errInfo)


def test_download_content_thumbnail_success(mocker):
    """Tests successful downloading of content thumbnail."""
    mock_content_details = {"result": {"content": {"posterImage": "https://dev.test.com/content/original_url.png"}}}
    mock_thumbnail_url = "formatted_url"
    mock_thumbnail_data = b"image_bytes"

    mock_fetch_details = mocker.patch("app.services.v1.image_variation.fetch_content_details", return_value=mock_content_details) 
    mock_format_url = mocker.patch("app.services.v1.image_variation.format_thumbnail_url", return_value=mock_thumbnail_url) 
    mock_download_thumb = mocker.patch("app.services.v1.image_variation.download_thumbnail", return_value=mock_thumbnail_data)

    content_id = "test_content_456"

    url, data = download_content_thumbnail(content_id)

    mock_fetch_details.assert_called_once_with(content_id)
    mock_format_url.assert_called_once_with(mock_content_details)
    mock_download_thumb.assert_called_once_with(mock_thumbnail_url)
    assert url == mock_thumbnail_url
    assert data == mock_thumbnail_data

def test_download_content_thumbnail_exception(mocker):
    """Tests handling of TypeError."""

    with pytest.raises(TypeError) as errInfo:
        download_content_thumbnail()

    assert "missing 1 required positional argument" in str(errInfo)


def test_download_content_thumbnail_error_propagation(mocker):
    """Tests error propagation from dependencies in download_content_thumbnail."""
    mock_fetch_details = mocker.patch("app.services.v1.image_variation.fetch_content_details", side_effect=Exception("Fetch error")) 
    mock_format_url = mocker.patch("app.services.v1.image_variation.format_thumbnail_url") 
    mock_download_thumb = mocker.patch("app.services.v1.image_variation.download_thumbnail") 

    content_id = "test_content_error_propagate"

    with pytest.raises(Exception, match="Fetch error"):
        download_content_thumbnail(content_id)

    mock_fetch_details.assert_called_once_with(content_id)
    mock_format_url.assert_not_called()
    mock_download_thumb.assert_not_called()

class MockPart:
    def __init__(self, content):
        self._content = content

    @classmethod
    def from_text(cls, text):
        return cls(text)

    @classmethod
    def from_image(cls, image):
        return cls(image)

class MockImage:
    def __init__(self, bytes_data):
        self._bytes_data = bytes_data

    @classmethod
    def from_bytes(cls, bytes_data):
        return cls(bytes_data)


class MockGenerativeModelResponse:
    def __init__(self, text):
        self.text = text

class MockGenerativeModel:
    def __init__(self, model_name, system_instruction=None):
        self.model_name = model_name
        self.system_instruction = system_instruction

    def generate_content(self, contents, generation_config=None, safety_settings=None, stream=False):
        # This method will be mocked in tests
        pass

def test_detect_logos_success(mocker):
    """Tests successful logo detection."""
    mock_image_data = b"9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEB"
    # with open("tests/services/v1/sample.jpg",'rb') as textfile:
    #     mock_image_data = textfile.read()
    mock_logo_response_text = '[{"logo_name": "MockLogo", "position": {"x": 10, "y": 20, "width": 50, "height": 30}, "confidence_score": 0.9}]'
    mock_logo_results = json.loads(mock_logo_response_text)

    mock_generate_content_method = MagicMock(return_value=MockGenerativeModelResponse(mock_logo_response_text))
    mock_generative_model_instance = MagicMock(spec=MockGenerativeModel)
    mock_generative_model_instance.generate_content = mock_generate_content_method
    mock_generative_model_class = mocker.patch("app.services.v1.image_variation.GenerativeModel", return_value=mock_generative_model_instance)

    mocker.patch("app.services.v1.image_variation.Part", side_effect=MockPart)
    mocker.patch("app.services.v1.image_variation.Image", side_effect=MockImage)

    results = detect_logos(mock_image_data)

    mock_generative_model_class.assert_called_once()
    mock_generate_content_method.assert_called_once()

    
    assert results == mock_logo_results

def test_generate_content_success(mocker):
    """Tests successful logo detection."""
    mock_image_data = b"9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEB"
    # with open("tests/services/v1/sample.jpg",'rb') as textfile:
    #     mock_image_data = textfile.read()
    mock_logo_response_text = 'cat standing on table'
    mock_logo_results = mock_logo_response_text

    mock_generate_content_method = MagicMock(return_value=MockGenerativeModelResponse(mock_logo_response_text))
    mock_generative_model_instance = MagicMock(spec=MockGenerativeModel)
    mock_generative_model_instance.generate_content = mock_generate_content_method
    mock_generative_model_class = mocker.patch("app.services.v1.image_variation.GenerativeModel", return_value=mock_generative_model_instance)

    mocker.patch("app.services.v1.image_variation.Part", side_effect=MockPart)
    mocker.patch("app.services.v1.image_variation.Image", side_effect=MockImage)

    results = generate_content(mock_image_data)

    mock_generative_model_class.assert_called_once()
    mock_generate_content_method.assert_called_once()
    
    assert results == mock_logo_results

def test_generate_content_exception(mocker):
    """Tests handling of TypeError."""

    with pytest.raises(TypeError) as errInfo:
        generate_content()

    assert "missing 1 required positional argument" in str(errInfo)