import logging
from fastapi import APIRouter, HTTPException, Request
from ..models import ImageResponse
from ..services.course import generate_course_summary, generate_image_prompt, generate_image

logger = logging.getLogger("kb-image-api")
router = APIRouter(
    prefix="/course",
    tags=["Course"]
)

@router.get("/{course_id}", response_model=ImageResponse)
def generate_course_image(course_id: str):
    try:
        final_summary = generate_course_summary(course_id)
        image_prompt = generate_image_prompt(final_summary)
        image_url = generate_image(image_prompt)
        return {
            "final_summary": final_summary,
            "image_prompt": image_prompt,
            "image_url": image_url
        }
    except Exception as e:
        logger.exception("Error while generating the image")
        raise HTTPException(status_code=500, detail=str(e))
    