from typing import Optional, Sequence
from fastapi import HTTPException, status
from sqlmodel import Session

from models.entities import Libro, LibroCreate, LibroUpdate
from repositories import autores as repo_autores
from repositories import libros as repo_libros


def get_libros(session: Session, disponibles: Optional[bool] = None) -> Sequence[Libro]:
    return repo_libros.get_all(session, disponibles=disponibles)


def get_libro_by_id(session: Session, libro_id: int) -> Libro:
    libro = repo_libros.get_by_id(session, libro_id)
    if not libro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Libro con id {libro_id} no encontrado",
        )
    return libro


def create_libro(session: Session, libro_in: LibroCreate) -> Libro:
    # Regla 8: ISBN duplicado -> 409
    existente = repo_libros.get_by_isbn(session, libro_in.isbn)
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un libro con el ISBN '{libro_in.isbn}'",
        )
    return repo_libros.create(session, libro_in)


def update_libro(session: Session, libro_id: int, libro_in: LibroUpdate) -> Libro:
    libro = get_libro_by_id(session, libro_id)

    # Regla 8: Chequear ISBN duplicado en otro libro
    if libro_in.isbn is not None and libro_in.isbn != libro.isbn:
        duplicado = repo_libros.get_by_isbn(session, libro_in.isbn, exclude_id=libro_id)
        if duplicado:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe otro libro con el ISBN '{libro_in.isbn}'",
            )
    return repo_libros.update(session, libro, libro_in)


def delete_libro(session: Session, libro_id: int) -> None:
    libro = get_libro_by_id(session, libro_id)
    repo_libros.delete(session, libro)


def asociar_autor_a_libro(session: Session, libro_id: int, autor_id: int) -> Libro:
    # Regla 7: Recurso inexistente (Libro o Autor)
    libro = get_libro_by_id(session, libro_id)
    autor = repo_autores.get_by_id(session, autor_id)
    if not autor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Autor con id {autor_id} no encontrado",
        )

    asociacion = repo_libros.get_asociacion(session, libro_id, autor_id)
    if not asociacion:
        repo_libros.asociar_autor(session, libro_id, autor_id)

    session.refresh(libro)
    return libro
