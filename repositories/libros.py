from typing import Optional, Sequence
from sqlmodel import Session, select

from models.entities import Libro, LibroAutor, LibroCreate, LibroUpdate


def get_all(session: Session, disponibles: Optional[bool] = None) -> Sequence[Libro]:
    query = select(Libro)
    if disponibles is True:
        query = query.where(Libro.stock > 0)
    elif disponibles is False:
        query = query.where(Libro.stock == 0)
    return session.exec(query).all()


def get_by_id(session: Session, libro_id: int) -> Libro | None:
    return session.get(Libro, libro_id)


def get_by_isbn(session: Session, isbn: str, exclude_id: Optional[int] = None) -> Libro | None:
    query = select(Libro).where(Libro.isbn == isbn)
    if exclude_id is not None:
        query = query.where(Libro.id != exclude_id)
    return session.exec(query).first()


def create(session: Session, libro_in: LibroCreate) -> Libro:
    libro = Libro.model_validate(libro_in)
    session.add(libro)
    session.commit()
    session.refresh(libro)
    return libro


def update(session: Session, libro: Libro, libro_in: LibroUpdate) -> Libro:
    update_data = libro_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(libro, key, value)
    session.add(libro)
    session.commit()
    session.refresh(libro)
    return libro


def delete(session: Session, libro: Libro) -> None:
    session.delete(libro)
    session.commit()


def get_asociacion(session: Session, libro_id: int, autor_id: int) -> LibroAutor | None:
    return session.exec(
        select(LibroAutor).where(
            LibroAutor.libro_id == libro_id,
            LibroAutor.autor_id == autor_id,
        )
    ).first()


def asociar_autor(session: Session, libro_id: int, autor_id: int) -> None:
    asoc = LibroAutor(libro_id=libro_id, autor_id=autor_id)
    session.add(asoc)
    session.commit()


def save(session: Session, libro: Libro) -> Libro:
    session.add(libro)
    session.commit()
    session.refresh(libro)
    return libro
