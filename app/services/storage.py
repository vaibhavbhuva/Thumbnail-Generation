from google.cloud import storage
from google.oauth2 import service_account


#setting credential for google storage service account
credentials = service_account.Credentials.from_service_account_file("creds/storage_key.json")

def upload_blob(bucket_name, source_file_name, destination_blob_name, project):
    """Uploads a file to the bucket."""

    storage_client = storage.Client(project=project, credentials=credentials)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

  

    #blob.upload_from_filename(source_file_name, if_generation_match=generation_match_precondition)
    # not setting generation_match_precondition as 0 to allow overwriting of thumbnails.
    blob.upload_from_filename(source_file_name)

    blob.make_public()
    print(blob.public_url)
    print(
        f"File {source_file_name} uploaded to {destination_blob_name}."
    )
    return blob.public_url

