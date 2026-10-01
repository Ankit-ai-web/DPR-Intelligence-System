from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Original filename uploaded by the user
    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # Unique filename used for physical storage
    stored_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # Physical path of the stored file
    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    # MIME type
    file_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    # File size in bytes
    file_size: Mapped[int] = mapped_column(
        nullable=False
    )

    # Number of pages
    pages: Mapped[int] = mapped_column(
        nullable=False
    )

    # Extracted text
    text: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    # Processing status
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="uploaded"
    )

    # Associated DPR project
    project_id: Mapped[int | None] = mapped_column(
        ForeignKey("dpr_projects.id"),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    project: Mapped["DPRProject | None"] = relationship()