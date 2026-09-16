from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.dpr_project import (
    DPRProjectCreate,
    DPRProjectResponse,
)
from app.services.dpr_project_service import (
    create_project,
    get_project,
    get_user_projects,
)

router = APIRouter(
    prefix="/projects",
    tags=["DPR Projects"],
)


@router.post(
    "/user/{user_id}",
    response_model=DPRProjectResponse,
    status_code=201,
)
def create_project_route(
    user_id: int,
    project_data: DPRProjectCreate,
    db: Session = Depends(get_db),
):
    return create_project(
        db,
        project_data,
        user_id,
    )


@router.get(
    "/{project_id}",
    response_model=DPRProjectResponse,
)
def get_project_route(
    project_id: int,
    db: Session = Depends(get_db),
):
    project = get_project(db, project_id)

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    return project


@router.get(
    "/user/{user_id}",
    response_model=list[DPRProjectResponse],
)
def list_user_projects(
    user_id: int,
    db: Session = Depends(get_db),
):
    return get_user_projects(db, user_id)