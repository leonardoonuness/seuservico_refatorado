"""
routes/admin.py — Painel administrativo
"""
import logging
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.dependencies import require_admin
from app.db.session import get_db
from app.models.user import User
from app.models.professional import Professional
from app.models.service_request import ServiceRequest
from app.models.review import Review

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard/stats", summary="Métricas gerais")
def dashboard_stats(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return {
        "total_users": db.query(User).count(),
        "total_professionals": db.query(User).filter(User.user_type == "professional").count(),
        "total_clients": db.query(User).filter(User.user_type == "client").count(),
        "total_services": db.query(ServiceRequest).count(),
        "completed_services": db.query(ServiceRequest).filter(ServiceRequest.status == "completed").count(),
        "pending_services": db.query(ServiceRequest).filter(ServiceRequest.status == "pending").count(),
        "total_reviews": db.query(Review).count(),
        "reported_reviews": db.query(Review).filter(Review.is_reported == True).count(),
        "premium_professionals": db.query(Professional).filter(Professional.is_premium == True).count(),
    }


@router.get("/professionals/pending", summary="Profissionais aguardando aprovação")
def pending_professionals(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return (
        db.query(Professional)
        .join(User, Professional.user_id == User.id)
        .filter(User.is_verified == False, User.is_blocked == False)
        .offset((page - 1) * size).limit(size).all()
    )


@router.put("/professionals/{professional_id}/verify", summary="Aprovar profissional")
def verify_professional(
    professional_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    from datetime import datetime, timezone
    prof = db.query(Professional).filter(Professional.id == professional_id).first()
    if not prof:
        raise HTTPException(404, "Profissional não encontrado.")
    user = db.query(User).filter(User.id == prof.user_id).first()
    user.is_verified = True
    prof.verified_at = datetime.now(timezone.utc)
    prof.verified_by = admin.id
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.exception("Erro ao verificar profissional: %s", exc)
        raise HTTPException(500, "Erro interno.")
    db.refresh(prof)
    return prof


@router.put("/professionals/{professional_id}/feature", summary="Destacar profissional")
def feature_professional(
    professional_id: str,
    featured: bool = Query(True),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    prof = db.query(Professional).filter(Professional.id == professional_id).first()
    if not prof:
        raise HTTPException(404, "Profissional não encontrado.")
    prof.is_premium = featured
    db.commit()
    db.refresh(prof)
    return prof


@router.get("/users", summary="Listar todos os usuários")
def list_users(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return db.query(User).order_by(User.created_at.desc()).offset((page - 1) * size).limit(size).all()


@router.put("/users/{user_id}/block", summary="Bloquear usuário")
def block_user(
    user_id: str,
    data: dict,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "Usuário não encontrado.")
    user.is_blocked = True
    user.block_reason = data.get("reason", "")
    db.commit()
    db.refresh(user)
    return user


@router.get("/reviews/reported", summary="Avaliações reportadas")
def reported_reviews(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return (
        db.query(Review)
        .filter(Review.is_reported == True, Review.is_removed == False)
        .order_by(Review.created_at.desc())
        .offset((page - 1) * size).limit(size).all()
    )


@router.put("/reviews/{review_id}/moderate", summary="Moderar avaliação")
def moderate_review(
    review_id: str,
    data: dict,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(404, "Avaliação não encontrada.")
    action = data.get("action", "keep")
    if action == "remove":
        review.is_removed = True
        review.removal_reason = data.get("reason")
    else:
        review.is_reported = False
    db.commit()
    db.refresh(review)
    return review


@router.get("/reports/metrics", summary="Métricas detalhadas")
def report_metrics(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    avg_rating = db.query(func.avg(Review.rating)).scalar() or 0
    return {
        "new_users": db.query(User).count(),
        "new_services": db.query(ServiceRequest).count(),
        "completed_services": db.query(ServiceRequest).filter(ServiceRequest.status == "completed").count(),
        "cancelled_services": db.query(ServiceRequest).filter(ServiceRequest.status == "cancelled").count(),
        "average_rating": round(float(avg_rating), 2),
    }
