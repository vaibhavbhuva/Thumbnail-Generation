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

4. Create a `.env` file in the root directory and set your OpenAI API key:
    ```
    OPENAI_API_KEY=your_openai_api_key_here
    ```  

## Usage

• Run the FastAPI application:
`uvicorn app.main:app --reload`

• Access the API at http://localhost:8000/docs.

Use the `/v1/image/course/{course_id}` endpoint to generate image.


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