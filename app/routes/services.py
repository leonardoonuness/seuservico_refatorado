"""
routes/services.py — Solicitações de serviço
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.service_request import ServiceRequest
from app.models.professional import Professional
from app.models.review import Review

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/services", tags=["Serviços"])

# ── Helpers ────────────────────────────────────────────────────────────────────

def _get_request_or_404(db: Session, request_id: str) -> ServiceRequest:
    req = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Serviço não encontrado.")
    return req


def _commit(db: Session, label: str) -> None:
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.exception("Erro ao salvar %s: %s", label, exc)
        raise HTTPException(status_code=500, detail="Erro interno ao salvar.")


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post("/requests", status_code=201, summary="Criar solicitação")
def create_request(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    req = ServiceRequest(
        client_id=current_user.id,
        professional_id=data.get("professional_id"),
        category=data["category"],
        service=data["service"],
        description=data.get("description"),
        address=data["address"],
        city=data["city"],
        latitude=data.get("latitude"),
        longitude=data.get("longitude"),
        scheduled_date=data.get("scheduled_date"),
        price=data.get("price"),
    )
    db.add(req)
    _commit(db, "service_request")
    db.refresh(req)
    return req


@router.get("/requests/client", summary="Serviços do cliente")
def client_requests(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = (
        db.query(ServiceRequest)
        .filter(ServiceRequest.client_id == current_user.id)
        .order_by(ServiceRequest.created_at.desc())
        .offset((page - 1) * size).limit(size).all()
    )
    return items


@router.get("/requests/professional", summary="Serviços do profissional")
def professional_requests(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = (
        db.query(ServiceRequest)
        .filter(ServiceRequest.professional_id == current_user.id)
        .order_by(ServiceRequest.created_at.desc())
        .offset((page - 1) * size).limit(size).all()
    )
    return items


@router.get("/requests/{request_id}", summary="Detalhes do serviço")
def get_request(
    request_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    req = _get_request_or_404(db, request_id)
    if req.client_id != current_user.id and req.professional_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado.")
    return req


def _transition(db: Session, req: ServiceRequest, target: str) -> ServiceRequest:
    req.status = target
    _commit(db, f"status->{target}")
    db.refresh(req)
    return req


@router.put("/requests/{request_id}/accept")
def accept(request_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    req = _get_request_or_404(db, request_id)
    if req.status != "pending":
        raise HTTPException(400, "Solicitação não está pendente.")
    if not req.professional_id:
        req.professional_id = current_user.id
    return _transition(db, req, "accepted")


@router.put("/requests/{request_id}/reject")
def reject(request_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    req = _get_request_or_404(db, request_id)
    if req.professional_id != current_user.id:
        raise HTTPException(403, "Acesso negado.")
    return _transition(db, req, "cancelled")


@router.put("/requests/{request_id}/start")
def start(request_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    req = _get_request_or_404(db, request_id)
    if req.professional_id != current_user.id:
        raise HTTPException(403, "Acesso negado.")
    if req.status != "accepted":
        raise HTTPException(400, "Serviço precisa estar aceito primeiro.")
    return _transition(db, req, "in_progress")


@router.put("/requests/{request_id}/complete")
def complete(request_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    req = _get_request_or_404(db, request_id)
    if req.professional_id != current_user.id:
        raise HTTPException(403, "Acesso negado.")
    if req.status != "in_progress":
        raise HTTPException(400, "Serviço não está em andamento.")
    return _transition(db, req, "completed")


@router.put("/requests/{request_id}/cancel")
def cancel(request_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    req = _get_request_or_404(db, request_id)
    if req.client_id != current_user.id and req.professional_id != current_user.id:
        raise HTTPException(403, "Acesso negado.")
    if req.status in ("completed", "cancelled"):
        raise HTTPException(400, "Não é possível cancelar este serviço.")
    return _transition(db, req, "cancelled")


@router.post("/requests/{request_id}/rate", status_code=201)
def rate(
    request_id: str,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    req = _get_request_or_404(db, request_id)
    if req.client_id != current_user.id:
        raise HTTPException(403, "Apenas o cliente pode avaliar.")
    if req.status != "completed":
        raise HTTPException(400, "Serviço não foi concluído.")
    if db.query(Review).filter(Review.service_request_id == req.id).first():
        raise HTTPException(409, "Serviço já avaliado.")

    rating_val = int(data.get("rating", 0))
    if not 1 <= rating_val <= 5:
        raise HTTPException(422, "Nota deve ser entre 1 e 5.")

    review = Review(
        service_request_id=req.id,
        client_id=current_user.id,
        professional_id=req.professional_id,
        rating=rating_val,
        comment=data.get("comment"),
    )
    db.add(review)

    # Recalcula rating do profissional
    prof = db.query(Professional).filter(Professional.user_id == req.professional_id).first()
    if prof:
        total = prof.total_ratings + 1
        prof.rating = round(((prof.rating * prof.total_ratings) + rating_val) / total, 2)
        prof.total_ratings = total

    _commit(db, "review")
    db.refresh(review)
    return review
