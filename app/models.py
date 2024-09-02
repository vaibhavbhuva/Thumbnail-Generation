from pydantic import BaseModel

class ImageResponse(BaseModel):
    final_summary: str
    image_prompt: str
    image_url: str