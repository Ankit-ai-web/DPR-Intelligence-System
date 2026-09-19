from datetime import datetime

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: int
    filename: str
    pages: int
    text: str
    project_id: int | None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class DocumentListResponse(BaseModel):
    id: int
    filename: str
    pages: int
    project_id: int | None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }