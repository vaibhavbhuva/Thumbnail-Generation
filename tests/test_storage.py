import pytest
from unittest import mock
from unittest.mock import MagicMock, patch
from app.libs.storage import GCPStorage

@patch("app.libs.storage.os.getenv")
@patch("app.libs.storage.service_account.Credentials.from_service_account_file")
@patch("app.libs.storage.storage.Client")
def test_gcp_storage_initialization(mock_storage_client, mock_credentials, mock_getenv):
    mock_getenv.side_effect = lambda key: {
        "GCP_BUCKET_NAME": "test-bucket",
        "GCP_STORAGE_CREDENTIALS": "/fake/credentials.json"
    }.get(key)

    instance = GCPStorage()

    mock_credentials.assert_called_once_with("/fake/credentials.json")
    mock_storage_client.assert_called_once()
    assert instance.__bucket_name__ == "test-bucket"
    assert instance.__client__ is not None

@patch("app.libs.storage.os.getenv", return_value=None)
def test_gcp_storage_init_missing_env_vars(mock_getenv):
    with pytest.raises(ValueError, match="GCPStorage client not initialized. Missing google bucket_name or crendentials"):
        GCPStorage()

@patch("app.libs.storage.os.getenv")
@patch("app.libs.storage.service_account.Credentials.from_service_account_file")
@patch("app.libs.storage.storage.Client")
def test_write_file_success(mock_storage_client, mock_credentials, mock_getenv):
    mock_getenv.side_effect = lambda key: {
        "GCP_BUCKET_NAME": "test-bucket",
        "GCP_STORAGE_CREDENTIALS": "/fake/credentials.json"
    }.get(key)

    mock_blob = MagicMock()
    mock_bucket = MagicMock()
    mock_bucket.blob.return_value = mock_blob
    mock_storage_client.return_value.bucket.return_value = mock_bucket

    storage_instance = GCPStorage()
    storage_instance.write_file("image.jpg", b"data")

    mock_blob.upload_from_string.assert_called_once_with(b"data", content_type="image/jpeg")

@patch("app.libs.storage.os.getenv")
@patch("app.libs.storage.service_account.Credentials.from_service_account_file")
@patch("app.libs.storage.storage.Client")
def test_public_url(mock_storage_client, mock_credentials, mock_getenv):
    mock_getenv.side_effect = lambda key: {
        "GCP_BUCKET_NAME": "test-bucket",
        "GCP_STORAGE_CREDENTIALS": "/fake/credentials.json"
    }.get(key)

    fake_url = "https://fake.public.url"
    mock_blob = MagicMock()
    mock_blob.public_url = fake_url

    mock_bucket = MagicMock()
    mock_bucket.blob.return_value = mock_blob
    mock_storage_client.return_value.bucket.return_value = mock_bucket

    instance = GCPStorage()
    result = instance.public_url("file.png")

    mock_blob.make_public.assert_called_once()
    assert result == fake_url

@patch("app.libs.storage.os.getenv")
@patch("app.libs.storage.service_account.Credentials.from_service_account_file")
@patch("app.libs.storage.storage.Client")
def test_write_file_raises_without_client(mock_storage_client, mock_credentials, mock_getenv):
    mock_getenv.side_effect = lambda key: {
        "GCP_BUCKET_NAME": "test-bucket",
        "GCP_STORAGE_CREDENTIALS": "/fake/credentials.json"
    }.get(key)

    instance = GCPStorage()
    instance.__client__ = None

    with pytest.raises(Exception, match="GCPSyncStorage client not initialized"):
        instance.write_file("file.png", b"data")

@patch("app.libs.storage.os.getenv")
@patch("app.libs.storage.service_account.Credentials.from_service_account_file")
@patch("app.libs.storage.storage.Client")
def test_public_url_raises_without_client(mock_storage_client, mock_credentials, mock_getenv):
    mock_getenv.side_effect = lambda key: {
        "GCP_BUCKET_NAME": "test-bucket",
        "GCP_STORAGE_CREDENTIALS": "/fake/credentials.json"
    }.get(key)

    instance = GCPStorage()
    instance.__client__ = None

    with pytest.raises(Exception, match="GCP Storage client not initialized"):
        instance.public_url("file.png")
