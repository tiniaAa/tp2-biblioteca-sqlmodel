from typing import Optional, Sequence
from fastapi import HTTPException, status
from sqlmodel import Session

from models.entities import Prestamo, Socio, SocioCreate, SocioUpdate
from repositories import prestamos as repo_prestamos
from repositories import socios as repo_socios


def get_socios(session: Session) -> Sequence[Socio]:
    return repo_socios.get_all(session)


def get_socio_by_id(session: Session, socio_id: int) -> Socio:
    socio = repo_socios.get_by_id(session, socio_id)
    if not socio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Socio con id {socio_id} no encontrado",
        )
    return socio


def create_socio(session: Session, socio_in: SocioCreate) -> Socio:
    # Regla 8: Email duplicado -> 409
    existente = repo_socios.get_by_email(session, socio_in.email)
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un socio con el email '{socio_in.email}'",
        )
    return repo_socios.create(session, socio_in)


def update_socio(session: Session, socio_id: int, socio_in: SocioUpdate) -> Socio:
    socio = get_socio_by_id(session, socio_id)

    # Regla 8: Chequear email duplicado en otro socio
    if socio_in.email is not None and socio_in.email != socio.email:
        duplicado = repo_socios.get_by_email(session, socio_in.email, exclude_id=socio_id)
        if duplicado:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe otro socio con el email '{socio_in.email}'",
            )
    return repo_socios.update(session, socio, socio_in)


def delete_socio(session: Session, socio_id: int) -> None:
    socio = get_socio_by_id(session, socio_id)
    repo_socios.delete(session, socio)


def get_prestamos_by_socio(
    session: Session, socio_id: int, activos: Optional[bool] = None
) -> Sequence[Prestamo]:
    # Regla 7: Recurso inexistente (Socio)
    get_socio_by_id(session, socio_id)
    return repo_prestamos.get_by_socio(session, socio_id, activos=activos)
