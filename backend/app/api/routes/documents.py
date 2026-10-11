import json
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy import select,delete
from sqlalchemy.orm import Session
import fitz

from app.db.database import get_db
from app.models.document import Document
from app.models.dpr_project import DPRProject
from app.models.analysis import DocumentAnalysis
from app.schemas.document import DocumentResponse, DocumentListResponse
from app.services.ai_analysis import analyze_dpr


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
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    if project_id is not None:
        project = db.get(DPRProject, project_id)

        if not project:
            raise HTTPException(
                status_code=404,
                detail="DPR Project not found"
            )

    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty"
        )

    original_filename = file.filename or "document.pdf"

    stored_filename = f"{uuid4().hex}.pdf"

    file_path = UPLOAD_DIR / stored_filename

    try:
        file_path.write_bytes(contents)

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to save uploaded file"
        )

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

    extracted_text = ""

    for page in pdf:
        extracted_text += page.get_text()

    page_count = len(pdf)

    pdf.close()

    if not extracted_text.strip():
        file_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=422,
            detail="No readable text found in PDF. The PDF may be scanned or image-based."
        )

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


# =========================
# ANALYZE DOCUMENT WITH AI
# =========================

@router.post("/{document_id}/analyze")
def analyze_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    document = db.get(Document, document_id)

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    if not document.text or not document.text.strip():
        raise HTTPException(
            status_code=422,
            detail="Document has no extracted text"
        )

    # =========================
    # GENERATE AI ANALYSIS
    # =========================

    try:
        analysis = analyze_dpr(document.text)

        parsed_analysis = json.loads(analysis)

    except json.JSONDecodeError as e:
        print("AI JSON ERROR:", repr(e))

        raise HTTPException(
            status_code=500,
            detail="AI returned invalid analysis data"
        )

    except Exception as e:
        print("AI ANALYSIS ERROR:", repr(e))

        raise HTTPException(
            status_code=500,
            detail="Failed to analyze document with AI"
        )

    # =========================
    # EXTRACT INTELLIGENCE SCORES
    # =========================

    health_score = parsed_analysis.get(
        "health_score",
        0
    )

    risk_score = parsed_analysis.get(
        "risk_score",
        0
    )

    data_completeness = parsed_analysis.get(
        "data_completeness",
        0
    )

    risk_level = parsed_analysis.get(
        "risk_level",
        "Unknown"
    )

    # =========================
    # SAVE ANALYSIS
    # =========================

    try:
        document_analysis = DocumentAnalysis(
            document_id=document.id,
            analysis=analysis,
            health_score=health_score,
            risk_score=risk_score,
            data_completeness=data_completeness,
            risk_level=risk_level
        )

        db.add(document_analysis)
        db.commit()
        db.refresh(document_analysis)

    except Exception as e:
        db.rollback()

        print("ANALYSIS DATABASE ERROR:", repr(e))

        raise HTTPException(
            status_code=500,
            detail="AI analysis generated but failed to save it"
        )

    # =========================
    # RESPONSE
    # =========================

    return {
        "document_id": document.id,
        "analysis_id": document_analysis.id,
        "filename": document.filename,
        "status": "analyzed",

        "scores": {
            "health_score": document_analysis.health_score,
            "risk_score": document_analysis.risk_score,
            "data_completeness": document_analysis.data_completeness,
            "risk_level": document_analysis.risk_level
        },

        "analysis": parsed_analysis,
        "created_at": document_analysis.created_at
    }


# =========================
# GET SAVED ANALYSIS
# =========================

@router.get("/{document_id}/analysis")
def get_document_analysis(
    document_id: int,
    db: Session = Depends(get_db)
):
    # =========================
    # CHECK DOCUMENT EXISTS
    # =========================

    document = db.get(Document, document_id)

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    # =========================
    # GET LATEST ANALYSIS
    # =========================

    analysis = db.scalars(
        select(DocumentAnalysis)
        .where(
            DocumentAnalysis.document_id == document_id
        )
        .order_by(
            DocumentAnalysis.created_at.desc()
        )
    ).first()

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="No analysis found for this document"
        )

    # =========================
    # RESPONSE
    # =========================

    return {
        "document_id": document.id,
        "filename": document.filename,
        "analysis_id": analysis.id,

        "scores": {
            "health_score": analysis.health_score,
            "risk_score": analysis.risk_score,
            "data_completeness": analysis.data_completeness,
            "risk_level": analysis.risk_level
        },

        "analysis": json.loads(analysis.analysis),
        "created_at": analysis.created_at
    }

@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = db.get(Document, document_id)

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    saved_file_path = Path(document.file_path)

    try:
        db.execute(
            delete(DocumentAnalysis).where(
                DocumentAnalysis.document_id == document_id
            )
        )
        db.delete(document)
        db.commit()

    except Exception as e:
        db.rollback()
        print("DOCUMENT DELETE ERROR:", repr(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to delete document from database",
        )

    try:
        upload_root = UPLOAD_DIR.resolve()
        resolved_path = saved_file_path.resolve()

        if resolved_path.parent == upload_root:
            resolved_path.unlink(missing_ok=True)
    except OSError as e:
        print("PDF CLEANUP ERROR:", repr(e))

    return {
        "message": "Document deleted successfully",
        "document_id": document_id,
    }