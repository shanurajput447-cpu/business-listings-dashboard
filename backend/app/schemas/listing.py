from pydantic import BaseModel, Field


class ListingCreate(BaseModel):
    """Incoming listing payload for bulk insert."""

    business_name: str = Field(..., min_length=1, max_length=255)
    category: str | None = Field(default=None, max_length=150)
    city: str | None = Field(default=None, max_length=100)
    address: str | None = Field(default=None)
    phone: str | None = Field(default=None, max_length=30)
    source: str | None = Field(default=None, max_length=100)


class ListingBulkCreate(BaseModel):
    listings: list[ListingCreate] = Field(..., min_length=1)


class ListingBulkInsertResponse(BaseModel):
    success: bool
    inserted_count: int


class CityCountItem(BaseModel):
    city: str
    count: int


class CategoryCountItem(BaseModel):
    category: str
    count: int


class SourceCountItem(BaseModel):
    source: str
    count: int
