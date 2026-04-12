"""
routes/professionals.py
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_professional
from app.db.session import get_db
from app.models.user import User
from app.models.professional import Professional

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/professionals", tags=["Profissionais"])


@router.get("/", summary="Listar profissionais com filtros")
def list_professionals(
    category: Optional[str] = Query(None),
    service: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = (
        db.query(Professional)
        .join(User, Professional.user_id == User.id)
        .filter(User.is_blocked == False, User.is_active == True)
    )
    if city:
        query = query.filter(User.city.ilike(f"%{city}%"))
    if category:
        query = query.filter(Professional.categories.contains([category]))
    if service:
        query = query.filter(Professional.services.contains([service]))
    if min_rating is not None:
        query = query.filter(Professional.rating >= min_rating)

    total = query.count()
    items = (
        query
        .order_by(Professional.is_premium.desc(), Professional.rating.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    return {"total": total, "page": page, "size": size, "items": items}


@router.get("/{professional_id}", summary="Detalhes de um profissional")
def get_professional(professional_id: str, db: Session = Depends(get_db)):
    prof = db.query(Professional).filter(Professional.id == professional_id).first()
    if not prof:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profissional não encontrado.")
    return prof


@router.post("/register", status_code=status.HTTP_201_CREATED, summary="Criar perfil profissional")
def register_professional(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if db.query(Professional).filter(Professional.user_id == current_user.id).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Perfil profissional já existe.")
    prof = Professional(
        user_id=current_user.id,
        bio=data.get("bio"),
        experience=data.get("experience"),
        hourly_rate=data.get("hourly_rate"),
        categories=data.get("categories", []),
        services=data.get("services", []),
    )
    current_user.user_type = "professional"
    db.add(prof)
    try:
        db.commit()
        db.refresh(prof)
    except Exception as exc:
        db.rollback()
        logger.exception("Erro ao criar perfil profissional: %s", exc)
        raise HTTPException(status_code=500, detail="Erro ao criar perfil.")
    return prof
