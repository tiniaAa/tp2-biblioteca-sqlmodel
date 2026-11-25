from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from models.entities import PrestamoRead, Socio, SocioCreate, SocioRead, SocioUpdate
from repositories.database import get_session
from services import socios as service_socios

router = APIRouter(prefix="/socios", tags=["Socios"])


@router.post("", response_model=SocioRead, status_code=status.HTTP_201_CREATED)
def crear_socio(socio: SocioCreate, session: Session = Depends(get_session)) -> Socio:
    return service_socios.create_socio(session, socio)


@router.get("", response_model=list[SocioRead])
def listar_socios(session: Session = Depends(get_session)) -> list[Socio]:
    return list(service_socios.get_socios(session))


@router.get("/{id}", response_model=SocioRead)
def obtener_socio(id: int, session: Session = Depends(get_session)) -> Socio:
    return service_socios.get_socio_by_id(session, id)


@router.put("/{id}", response_model=SocioRead)
def actualizar_socio(
    id: int, socio_update: SocioUpdate, session: Session = Depends(get_session)
) -> Socio:
    return service_socios.update_socio(session, id, socio_update)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_socio(id: int, session: Session = Depends(get_session)) -> None:
    service_socios.delete_socio(session, id)
    return None


@router.get("/{id}/prestamos", response_model=list[PrestamoRead])
def listar_prestamos_socio(
    id: int,
    activos: Optional[bool] = Query(
        default=None,
        description="Filtrar préstamos activos (sin devolver) si es True",
    ),
    session: Session = Depends(get_session),
):
    return list(service_socios.get_prestamos_by_socio(session, id, activos=activos))
