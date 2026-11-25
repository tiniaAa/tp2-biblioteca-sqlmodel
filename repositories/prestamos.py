from datetime import date
from typing import Optional, Sequence
from sqlmodel import Session, select

from models.entities import Prestamo


def get_by_id(session: Session, prestamo_id: int) -> Prestamo | None:
    return session.get(Prestamo, prestamo_id)


def get_activos_by_socio(session: Session, socio_id: int) -> Sequence[Prestamo]:
    query = select(Prestamo).where(
        Prestamo.socio_id == socio_id,
        Prestamo.fecha_devolucion == None,  # noqa: E711
    )
    return session.exec(query).all()


def get_by_socio(
    session: Session, socio_id: int, activos: Optional[bool] = None
) -> Sequence[Prestamo]:
    query = select(Prestamo).where(Prestamo.socio_id == socio_id)
    if activos is True:
        query = query.where(Prestamo.fecha_devolucion == None)  # noqa: E711
    elif activos is False:
        query = query.where(Prestamo.fecha_devolucion != None)  # noqa: E711
    return session.exec(query).all()


def create(
    session: Session,
    socio_id: int,
    libro_id: int,
    fecha_prestamo: date,
    fecha_vencimiento: date,
) -> Prestamo:
    prestamo = Prestamo(
        socio_id=socio_id,
        libro_id=libro_id,
        fecha_prestamo=fecha_prestamo,
        fecha_vencimiento=fecha_vencimiento,
        fecha_devolucion=None,
        multa=0.0,
    )
    session.add(prestamo)
    session.commit()
    session.refresh(prestamo)
    return prestamo


def save(session: Session, prestamo: Prestamo) -> Prestamo:
    session.add(prestamo)
    session.commit()
    session.refresh(prestamo)
    return prestamo
