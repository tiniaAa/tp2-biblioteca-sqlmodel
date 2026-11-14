from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from models.entities import Prestamo, PrestamoRead, Socio, SocioCreate, SocioRead, SocioUpdate
from repositories.database import get_session

router = APIRouter(prefix="/socios", tags=["Socios"])


@router.post("", response_model=SocioRead, status_code=status.HTTP_201_CREATED)
def crear_socio(socio: SocioCreate, session: Session = Depends(get_session)) -> Socio:
    # Regla 8: Email duplicado -> 409
    existente = session.exec(select(Socio).where(Socio.email == socio.email)).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un socio con el email '{socio.email}'",
        )

    db_socio = Socio.model_validate(socio)
    session.add(db_socio)
    session.commit()
    session.refresh(db_socio)
    return db_socio


@router.get("", response_model=list[SocioRead])
def listar_socios(session: Session = Depends(get_session)) -> list[Socio]:
    socios = session.exec(select(Socio)).all()
    return list(socios)


@router.get("/{id}", response_model=SocioRead)
def obtener_socio(id: int, session: Session = Depends(get_session)) -> Socio:
    socio = session.get(Socio, id)
    if not socio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Socio con id {id} no encontrado",
        )
    return socio


@router.put("/{id}", response_model=SocioRead)
def actualizar_socio(
    id: int, socio_update: SocioUpdate, session: Session = Depends(get_session)
) -> Socio:
    socio = session.get(Socio, id)
    if not socio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Socio con id {id} no encontrado",
        )

    # Si se actualiza el email, chequear que no pertenezca a otro socio
    if socio_update.email is not None and socio_update.email != socio.email:
        duplicado = session.exec(
            select(Socio).where(Socio.email == socio_update.email, Socio.id != id)
        ).first()
        if duplicado:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe otro socio con el email '{socio_update.email}'",
            )

    update_data = socio_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(socio, key, value)
    session.add(socio)
    session.commit()
    session.refresh(socio)
    return socio


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_socio(id: int, session: Session = Depends(get_session)):
    socio = session.get(Socio, id)
    if not socio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Socio con id {id} no encontrado",
        )
    session.delete(socio)
    session.commit()
    return None


@router.get("/{id}/prestamos", response_model=list[PrestamoRead])
def listar_prestamos_socio(
    id: int,
    activos: Optional[bool] = Query(
        default=None,
        description="Filtrar préstamos activos (sin devolver) si es True",
    ),
    session: Session = Depends(get_session),
) -> list[Prestamo]:
    # Regla 7: Recurso inexistente (Socio)
    socio = session.get(Socio, id)
    if not socio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Socio con id {id} no encontrado",
        )

    query = select(Prestamo).where(Prestamo.socio_id == id)
    if activos is True:
        query = query.where(Prestamo.fecha_devolucion == None)  # noqa: E711
    elif activos is False:
        query = query.where(Prestamo.fecha_devolucion != None)  # noqa: E711

    prestamos = session.exec(query).all()
    return list(prestamos)
