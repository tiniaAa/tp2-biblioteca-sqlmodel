from typing import Sequence
from fastapi import HTTPException, status
from sqlmodel import Session

from models.entities import Autor, AutorCreate, AutorUpdate
from repositories import autores as repo_autores


def get_autores(session: Session) -> Sequence[Autor]:
    return repo_autores.get_all(session)


def get_autor_by_id(session: Session, autor_id: int) -> Autor:
    autor = repo_autores.get_by_id(session, autor_id)
    if not autor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Autor con id {autor_id} no encontrado",
        )
    return autor


def create_autor(session: Session, autor_in: AutorCreate) -> Autor:
    return repo_autores.create(session, autor_in)


def update_autor(session: Session, autor_id: int, autor_in: AutorUpdate) -> Autor:
    autor = get_autor_by_id(session, autor_id)
    return repo_autores.update(session, autor, autor_in)


def delete_autor(session: Session, autor_id: int) -> None:
    autor = get_autor_by_id(session, autor_id)
    repo_autores.delete(session, autor)
