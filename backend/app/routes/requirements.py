from math import ceil
from fastapi import APIRouter, HTTPException, Query, status
from app.models.requirement_models import (
    RequirementCreate, RequirementResponse, RequirementsList
)
from app.models.auth_models import ErrorResponse
from app.database.connection import execute_query
import pg8000.dbapi

router = APIRouter(prefix="/requirements", tags=["Requirements"])


# Shared column list for requirement read/write responses.
REQUIREMENT_FIELDS_SQL = """
    id,
    title,
    description,
    status,
    to_char(created_at, 'YYYY-MM-DD HH24:MI:SS') as created_at,
    to_char(updated_at, 'YYYY-MM-DD HH24:MI:SS') as updated_at
"""


# Maps a database row into the Pydantic response model.
def build_requirement_response(requirement: dict) -> RequirementResponse:
    return RequirementResponse(
        id=requirement['id'],
        title=requirement['title'],
        description=requirement['description'],
        status=requirement['status'],
        created_at=requirement['created_at'],
        updated_at=requirement['updated_at']
    )


def get_status_counts() -> dict[str, int]:
    status_rows = execute_query(
        """
        SELECT status, COUNT(*) AS count
        FROM app.requirements
        GROUP BY status
        """,
        fetch_all=True
    )
    if status_rows is None:
        status_rows = []

    status_counts = {
        "open": 0,
        "processed": 0,
        "obsolete": 0
    }
    for row in status_rows:
        status_counts[row["status"]] = row["count"]
    return status_counts


# Returns paginated requirements with status counts.
@router.get(
    "",
    response_model=RequirementsList,
    responses={500: {"model": ErrorResponse}}
)
def get_requirements(
    page: int = Query(1, ge=1, description="Page number to fetch"),
    limit: int = Query(10, ge=1, le=10000, description="Number of records per page")
):
    try:
        total_row = execute_query(
            "SELECT COUNT(*) AS total FROM app.requirements",
            fetch_one=True
        )
        total = total_row["total"] if total_row else 0
        total_pages = max(1, ceil(total / limit))
        page = min(page, total_pages)
        offset = (page - 1) * limit

        requirements = execute_query(
            f"""
            SELECT
                {REQUIREMENT_FIELDS_SQL}
            FROM app.requirements
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
            """,
            (limit, offset),
            fetch_all=True
        )
        
        if requirements is None:
            requirements = []
        
        return RequirementsList(
            requirements=[build_requirement_response(req) for req in requirements],
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
            status_counts=get_status_counts()
        )
    
    except Exception as e:
        print(f"Get requirements error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch requirements"
        )


# Returns every requirement only when the frontend explicitly selects "All".
@router.get(
    "/all",
    response_model=RequirementsList,
    responses={500: {"model": ErrorResponse}}
)
def get_all_requirements():
    try:
        total_row = execute_query(
            "SELECT COUNT(*) AS total FROM app.requirements",
            fetch_one=True
        )
        total = total_row["total"] if total_row else 0

        requirements = execute_query(
            f"""
            SELECT
                {REQUIREMENT_FIELDS_SQL}
            FROM app.requirements
            ORDER BY created_at DESC
            """,
            fetch_all=True
        )

        if requirements is None:
            requirements = []

        return RequirementsList(
            requirements=[build_requirement_response(req) for req in requirements],
            total=total,
            page=1,
            limit=total,
            total_pages=1,
            status_counts=get_status_counts()
        )

    except Exception as e:
        print(f"Get all requirements error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch requirements"
        )


# Creates a requirement after Pydantic and database status validation.
@router.post(
    "",
    response_model=RequirementResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
def create_requirement(request: RequirementCreate):
    try:
        result = execute_query(
            f"""
            INSERT INTO app.requirements (title, description, status)
            VALUES (%s, %s, %s)
            RETURNING
                {REQUIREMENT_FIELDS_SQL}
            """,
            (request.title, request.description, request.status.value),
            fetch_one=True
        )
        
        return build_requirement_response(result)
    
    except pg8000.dbapi.IntegrityError as e:
        if 'status' in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status. Must be 'open', 'processed', or 'obsolete'"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create requirement"
        )
    except Exception as e:
        print(f"Create requirement error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error while creating requirement"
        )


# Updates an existing requirement by id.
@router.patch(
    "/{requirement_id}",
    response_model=RequirementResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
def update_requirement(requirement_id: int, request: RequirementCreate):
    try:
        result = execute_query(
            f"""
            UPDATE app.requirements
            SET 
                title = %s,
                description = %s,
                status = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING
                {REQUIREMENT_FIELDS_SQL}
            """,
            (request.title, request.description, request.status.value, requirement_id),
            fetch_one=True
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Requirement not found"
            )
        
        return build_requirement_response(result)
    
    except HTTPException:
        raise
    except pg8000.dbapi.IntegrityError as e:
        if 'status' in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status. Must be 'open', 'processed', or 'obsolete'"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update requirement"
        )
    except Exception as e:
        print(f"Update requirement error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error while updating requirement"
        )


# Deletes an existing requirement by id.
@router.delete(
    "/{requirement_id}",
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
def delete_requirement(requirement_id: int):
    try:
        result = execute_query(
            "SELECT id FROM app.requirements WHERE id = %s",
            (requirement_id,),
            fetch_one=True
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Requirement not found"
            )
        
        execute_query(
            "DELETE FROM app.requirements WHERE id = %s",
            (requirement_id,)
        )
        
        return {"message": "Requirement deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete requirement error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error while deleting requirement"
        )
