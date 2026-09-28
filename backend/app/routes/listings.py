from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ListingBulkCreate, ListingBulkInsertResponse
from app.services.listings import bulk_insert_listings

router = APIRouter(prefix="/api/listings", tags=["listings"])


@router.post("/bulk", status_code=status.HTTP_201_CREATED)
def create_listings_bulk(
    payload: ListingBulkCreate,
    db: Session = Depends(get_db),
) -> ListingBulkInsertResponse:
    try:
        inserted_count = bulk_insert_listings(db, payload.listings)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to insert listings.",
        ) from exc

    return ListingBulkInsertResponse(success=True, inserted_count=inserted_count)
