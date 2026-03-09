from fastapi import APIRouter, HTTPException
from app.models.lusha_models import EnrichRequest, EnrichListRequest, LushaResult
from app.services.lusha_service import lusha_service
from app.config import settings

router = APIRouter(prefix="/enrich", tags=["enrich"])


@router.post("", response_model=LushaResult)
def enrich_single(request: EnrichRequest):
    """Enrich a single LinkedIn URL"""
    if not settings.LUSHA_API_KEY:
        raise HTTPException(status_code=500, detail="LUSHA_API_KEY not configured")

    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Enrich request for: {request.linkedin_url}")
    try:
        return lusha_service.enrich_person(
            request.linkedin_url,
            request.reveal_emails,
            request.reveal_phones,
            request.partial_profile
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/batch", response_model=list[LushaResult])
def enrich_batch(request: EnrichListRequest):
    """Enrich multiple LinkedIn URLs"""
    if not settings.LUSHA_API_KEY:
        raise HTTPException(status_code=500, detail="LUSHA_API_KEY not configured")

    if not request.urls:
        raise HTTPException(status_code=400, detail="No URLs provided")

    return lusha_service.enrich_list(request.urls)
