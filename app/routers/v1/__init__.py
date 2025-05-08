from fastapi import APIRouter
from .course import router as course_router
from .resource import router as resource_router

router = APIRouter(
    prefix="/v1/image"
)
router.include_router(course_router)
router.include_router(resource_router)