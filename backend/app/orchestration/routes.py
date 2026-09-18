from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.orchestration.schemas import DesignGenerateRequest, DesignGenerateResponse
from app.orchestration.service import DesignOrchestrator

router = APIRouter(prefix="/design", tags=["Design Orchestrator"])


@router.post("/generate", response_model=DesignGenerateResponse)
def generate_design(request: DesignGenerateRequest, db: Session = Depends(get_db)) -> DesignGenerateResponse:
    try:
        return DesignOrchestrator(db).generate(request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
