# Thumbnail Generation Service for KB Entities

This service utilizes generative AI to create visually appealing thumbnails for entities within the KB domain. By leveraging advanced language models and image generation techniques, this service provides a quick and efficient way to generate representative thumbnails for various KB entities.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- [Python 3.10+](https://www.python.org/downloads/)
- [Poetry](https://python-poetry.org/docs/#installation)
- [Docker](https://www.docker.com/get-started) (optional, for running the application in a container)


## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Docker](#docker)
- [Contributing](#contributing)


## Installation

1. Clone and Change the directory to the project root.

   ```bash
   git clone https://github.com/KB-iGOT/Thumbnail-Generation.git
   cd Thumbnail-Generation
   ```

2. Create a virtual environment (optional but recommended):
    ```
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    ```

3. Install the required dependencies:
    ```
    poetry install
    ```

4. Copy `.env.example` file, paste it into the same location, and rename to `.env` and update the values in that file.

    | **Environment Variable**          | **Description** |
    |-----------------------------------|-------------------------------------------------------------------------------------------------------|
    | `SERVICE_ENVIRONMENT`       | Specifies the environment in which the service is running. Can be "DEV", "STAGING", or "PROD".         |
    | `LOG_LEVEL`           | Defines the level of logging. Common values include "DEBUG", "INFO", "WARN", "ERROR".                 |
    | `KB_API_HOST=""` | Host URL for the KarmaYogi portal's API.                                                              |
    | **GCP Storage**                   | **Google Cloud Platform (GCP) Storage Configuration**                                                  |
    | `GCP_STORAGE_CREDENTIALS`      | Path to a JSON file containing GCP service account credentials for accessing Google Cloud Storage                               |
    | `GCP_BUCKET_NAME`              | Name of the GCP bucket where data is stored.                                                           |
    | `STORAGE_THUMBNAIL_FOLDER`     | Subfolder within the GCP bucket to store thumbnails of generated images. (e.g., `"thumbnail_images`")                                      |
    | `STORAGE_PROXY_PATH`           | Proxy path for accessing stored files in the GCP bucket through a proxy url. (e.g., `"thumbnails/generate"`)                                          |
    | **GCP Vertex AI**                 | **Google Cloud Platform (GCP) Vertex AI Configuration**                                                |
    | `GCP_GEMINI_CREDENTIALS`       | Path to the GCP Gemini credentials JSON file used for authentication with Vertex AI.                   |
    | `GCP_GEMINI_PROJECT_ID`        | ID of the GCP project where Vertex AI models are deployed.                                |
    | `GEMINI_MODEL_PRO` | Name of the Gemini text-to-image model to be used. (e.g., `"gemini-2.0-flash`")                         |
    | `VISION_MODEL` | Identifier for the vision model version to be used for image generation in Vertex AI. (e.g., `"imagen-3.0-fast-generate-001"`)              |
    | `NUMBER_OF_IMAGES`            | Defines the number of images to generate during an image processing task. (e.g., `"2"`)                             |


## Usage

• Run the FastAPI application:
`uvicorn app.main:app --reload`

• Access the API at http://localhost:8000/docs.

Use the `/v1/image/course/{course_id}` or `/v2/image/course/{course_id}` endpoint to generate image.


## Docker

To run the application using Docker, follow these steps:

- Build the Docker image: `docker build -t kb_image .`

- Run the Docker container: `docker run -d -p 8000:8000 --name kb_image_api kb_image`

Access the Application: You can access your FastAPI application by navigating to http://localhost:8000/docs in your web browser.

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, please open an issue or submit a pull request.

- Fork the repository.
- Create a new branch (e.g., `git checkout -b feature-branch`).
- Make your changes and commit them (e.g., `git commit -m 'Add new feature'`).
- Push to the branch (e.g., `git push origin feature-branch`).
- Open a pull request.