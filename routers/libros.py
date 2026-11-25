from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from models.entities import (
    Libro,
    LibroCreate,
    LibroRead,
    LibroReadWithAutores,
    LibroUpdate,
)
from repositories.database import get_session
from services import libros as service_libros

router = APIRouter(prefix="/libros", tags=["Libros"])


@router.post("", response_model=LibroRead, status_code=status.HTTP_201_CREATED)
def crear_libro(libro: LibroCreate, session: Session = Depends(get_session)) -> Libro:
    return service_libros.create_libro(session, libro)


@router.get("", response_model=list[LibroReadWithAutores])
def listar_libros(
    disponibles: Optional[bool] = Query(
        default=None,
        description="Filtrar por libros con stock > 0 si es True",
    ),
    session: Session = Depends(get_session),
) -> list[Libro]:
    return list(service_libros.get_libros(session, disponibles=disponibles))


@router.get("/{id}", response_model=LibroReadWithAutores)
def obtener_libro(id: int, session: Session = Depends(get_session)) -> Libro:
    return service_libros.get_libro_by_id(session, id)


@router.put("/{id}", response_model=LibroRead)
def actualizar_libro(
    id: int, libro_update: LibroUpdate, session: Session = Depends(get_session)
) -> Libro:
    return service_libros.update_libro(session, id, libro_update)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_libro(id: int, session: Session = Depends(get_session)) -> None:
    service_libros.delete_libro(session, id)
    return None


@router.post(
    "/{id}/autores/{autor_id}",
    response_model=LibroReadWithAutores,
    status_code=status.HTTP_200_OK,
)
def asociar_autor_a_libro(
    id: int, autor_id: int, session: Session = Depends(get_session)
) -> Libro:
    return service_libros.asociar_autor_a_libro(session, id, autor_id)
