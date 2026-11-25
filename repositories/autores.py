from typing import Sequence
from sqlmodel import Session, select

from models.entities import Autor, AutorCreate, AutorUpdate


def get_all(session: Session) -> Sequence[Autor]:
    return session.exec(select(Autor)).all()


def get_by_id(session: Session, autor_id: int) -> Autor | None:
    return session.get(Autor, autor_id)


def create(session: Session, autor_in: AutorCreate) -> Autor:
    autor = Autor.model_validate(autor_in)
    session.add(autor)
    session.commit()
    session.refresh(autor)
    return autor


def update(session: Session, autor: Autor, autor_in: AutorUpdate) -> Autor:
    update_data = autor_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(autor, key, value)
    session.add(autor)
    session.commit()
    session.refresh(autor)
    return autor


def delete(session: Session, autor: Autor) -> None:
    session.delete(autor)
    session.commit()
