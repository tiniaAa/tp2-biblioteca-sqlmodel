from typing import Optional, Sequence
from sqlmodel import Session, select

from models.entities import Socio, SocioCreate, SocioUpdate


def get_all(session: Session) -> Sequence[Socio]:
    return session.exec(select(Socio)).all()


def get_by_id(session: Session, socio_id: int) -> Socio | None:
    return session.get(Socio, socio_id)


def get_by_email(session: Session, email: str, exclude_id: Optional[int] = None) -> Socio | None:
    query = select(Socio).where(Socio.email == email)
    if exclude_id is not None:
        query = query.where(Socio.id != exclude_id)
    return session.exec(query).first()


def create(session: Session, socio_in: SocioCreate) -> Socio:
    socio = Socio.model_validate(socio_in)
    session.add(socio)
    session.commit()
    session.refresh(socio)
    return socio


def update(session: Session, socio: Socio, socio_in: SocioUpdate) -> Socio:
    update_data = socio_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(socio, key, value)
    session.add(socio)
    session.commit()
    session.refresh(socio)
    return socio


def delete(session: Session, socio: Socio) -> None:
    session.delete(socio)
    session.commit()
