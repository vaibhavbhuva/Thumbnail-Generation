import logging
from fastapi import APIRouter, HTTPException, Request
from ..models import ImageResponse
from ..services.course import generate_course_summary, generate_image_prompt, generate_image

logger = logging.getLogger("kb-image-api")
router = APIRouter(
    prefix="/resource",
    tags=["Resource"]
)

@router.get("/{resource_id}", response_model=dict)
def generate_image(resource_id: str):
    try:
        return {
            "msg": "This API is currently under development."
        }
    except Exception as e:
        print("Error while generating the image::", e)
        raise HTTPException(status_code=500, detail=str(e))
    