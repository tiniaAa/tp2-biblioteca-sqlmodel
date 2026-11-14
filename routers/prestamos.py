from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from models.entities import PrestamoCreate, PrestamoRead
from repositories.database import get_session
from services.prestamos import registrar_devolucion, registrar_prestamo

router = APIRouter(prefix="/prestamos", tags=["Préstamos"])


@router.post("", response_model=PrestamoRead, status_code=status.HTTP_201_CREATED)
def crear_prestamo(
    datos: PrestamoCreate,
    session: Session = Depends(get_session),
):
    return registrar_prestamo(session=session, datos=datos)


@router.post(
    "/{id}/devolucion",
    response_model=PrestamoRead,
    status_code=status.HTTP_200_OK,
)
def devolver_prestamo(
    id: int,
    session: Session = Depends(get_session),
):
    return registrar_devolucion(session=session, prestamo_id=id)
