from datetime import datetime

from pydantic import BaseModel


class DPRProjectCreate(BaseModel):
    title: str
    description: str | None = None


class DPRProjectResponse(BaseModel):
    id: int
    title: str
    description: str | None
    status: str
    user_id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }