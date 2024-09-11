from typing import List
from pydantic import BaseModel

class ImageResponse(BaseModel):
    final_summary: str
    image_prompt: str
    image_url: str

class ImageVariationResponse(BaseModel):
    images: List[str]