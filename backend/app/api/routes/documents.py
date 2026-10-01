from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
import fitz

from app.db.database import get_db
from app.models.document import Document
from app.models.dpr_project import DPRProject
from app.schemas.document import DocumentResponse, DocumentListResponse


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


# =========================
# UPLOAD DIRECTORY
# =========================

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# =========================
# UPLOAD DOCUMENT
# =========================

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    project_id: int | None = None,
    db: Session = Depends(get_db)
):
    # Check file type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    # Check project if project_id is provided
    if project_id is not None:
        project = db.get(DPRProject, project_id)

        if not project:
            raise HTTPException(
                status_code=404,
                detail="DPR Project not found"
            )

    # Read uploaded file
    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty"
        )

    # Original filename
    original_filename = file.filename or "document.pdf"

    # Generate unique filename for storage
    stored_filename = f"{uuid4().hex}.pdf"

    file_path = UPLOAD_DIR / stored_filename

    # Save original PDF
    try:
        file_path.write_bytes(contents)

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to save uploaded file"
        )

    # Open PDF
    try:
        pdf = fitz.open(
            stream=contents,
            filetype="pdf"
        )

    except Exception:
        file_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=400,
            detail="Invalid PDF file"
        )

    # Extract text
    extracted_text = ""

    for page in pdf:
        extracted_text += page.get_text()

    page_count = len(pdf)

    pdf.close()

    # Check if PDF contains readable text
    if not extracted_text.strip():
        file_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=422,
            detail="No readable text found in PDF. The PDF may be scanned or image-based."
        )

    # Create database document
    document = Document(
        filename=original_filename,
        stored_filename=stored_filename,
        file_path=str(file_path),
        file_type=file.content_type,
        file_size=len(contents),
        pages=page_count,
        text=extracted_text,
        status="processed",
        project_id=project_id
    )

    # Save document information
    try:
        db.add(document)
        db.commit()
        db.refresh(document)

    except Exception as e:
       db.rollback()
       file_path.unlink(missing_ok=True)
       print("DATABASE ERROR:", repr(e))
       raise HTTPException(
           status_code=500,
           detail="Failed to save document information"
    )

    # Return upload result
    return {
        "message": "Document uploaded successfully",
        "document_id": document.id,
        "filename": document.filename,
        "stored_filename": document.stored_filename,
        "pages": document.pages,
        "file_size": document.file_size,
        "text_length": len(document.text),
        "status": document.status,
        "project_id": document.project_id
    }


# =========================
# GET ALL DOCUMENTS
# =========================

@router.get(
    "/",
    response_model=list[DocumentListResponse]
)
def get_documents(
    db: Session = Depends(get_db)
):
    documents = db.scalars(
        select(Document)
    ).all()

    return documents


# =========================
# GET SINGLE DOCUMENT
# =========================

@router.get(
    "/{document_id}",
    response_model=DocumentResponse
)
def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    document = db.get(Document, document_id)

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return document