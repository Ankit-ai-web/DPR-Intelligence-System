from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.dpr_project import DPRProject
from app.schemas.dpr_project import DPRProjectCreate


def create_project(
    db: Session,
    project_data: DPRProjectCreate,
    user_id: int,
) -> DPRProject:

    project = DPRProject(
        title=project_data.title,
        description=project_data.description,
        user_id=user_id,
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project


def get_project(
    db: Session,
    project_id: int,
) -> DPRProject | None:

    return db.get(DPRProject, project_id)


def get_user_projects(
    db: Session,
    user_id: int,
) -> list[DPRProject]:

    result = db.execute(
        select(DPRProject)
        .where(DPRProject.user_id == user_id)
        .order_by(DPRProject.id)
    )

    return list(result.scalars().all())