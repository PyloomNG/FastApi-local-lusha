from fastapi import APIRouter, HTTPException
from app.services.bulk_service import bulk_service
from app.config import settings

router = APIRouter(prefix="/bulk", tags=["bulk"])


@router.post("/enrich")
def enrich_excel():
    """Enrich local Excel with Lusha data (Email, Phone, Company, Title, etc.)"""
    if not settings.LUSHA_API_KEY:
        raise HTTPException(status_code=500, detail="LUSHA_API_KEY not configured")

    try:
        data = bulk_service.enrich_excel(return_json=True)
        return {"status": "completed", "data": data}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
