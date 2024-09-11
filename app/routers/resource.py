import logging
from fastapi import APIRouter, HTTPException
from ..logger import logger
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
        logger.exception("Error while generating image for resource:")
        raise HTTPException(status_code=500, detail=str("Something went wrong, please try again later..."))
    