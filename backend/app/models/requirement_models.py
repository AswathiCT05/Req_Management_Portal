from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


# API-allowed requirement statuses.
class StatusEnum(str, Enum):
    OPEN = "open"
    PROCESSED = "processed"
    OBSOLETE = "obsolete"


# Validates new or updated requirement data.
class RequirementCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: StatusEnum = StatusEnum.OPEN
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Add login page",
                "description": "Create a login page with email/password",
                "status": "open"
            }
        }


# Shapes one requirement returned by the API.
class RequirementResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    created_at: str
    updated_at: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Add login page",
                "description": "Create a login page with email/password",
                "status": "open",
                "created_at": "2024-01-01T12:00:00",
                "updated_at": "2024-01-01T12:00:00"
            }
        }


# Shapes paginated requirement list responses.
class RequirementsList(BaseModel):
    requirements: list[RequirementResponse]
    total: int
    page: int = 1
    limit: int = 10
    total_pages: int = 1
    status_counts: dict[str, int] = {
        "open": 0,
        "processed": 0,
        "obsolete": 0
    }
    
    class Config:
        json_schema_extra = {
            "example": {
                "requirements": [
                    {
                        "id": 1,
                        "title": "Add login page",
                        "description": "Create a login page with email/password",
                        "status": "open",
                        "created_at": "2024-01-01T12:00:00",
                        "updated_at": "2024-01-01T12:00:00"
                    }
                ],
                "total": 1,
                "page": 1,
                "limit": 10,
                "total_pages": 1,
                "status_counts": {
                    "open": 1,
                    "processed": 0,
                    "obsolete": 0
                }
            }
        }
