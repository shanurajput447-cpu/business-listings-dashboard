from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import CategoryCountItem, CityCountItem, SourceCountItem
from app.services import dashboard as dashboard_service

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/city", response_model=list[CityCountItem])
def get_city_counts(db: Session = Depends(get_db)) -> list[CityCountItem]:
    try:
        return dashboard_service.get_city_counts(db)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load city dashboard counts.",
        ) from exc


@router.get("/category", response_model=list[CategoryCountItem])
def get_category_counts(db: Session = Depends(get_db)) -> list[CategoryCountItem]:
    try:
        return dashboard_service.get_category_counts(db)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load category dashboard counts.",
        ) from exc


@router.get("/source", response_model=list[SourceCountItem])
def get_source_counts(db: Session = Depends(get_db)) -> list[SourceCountItem]:
    try:
        return dashboard_service.get_source_counts(db)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load source dashboard counts.",
        ) from exc
