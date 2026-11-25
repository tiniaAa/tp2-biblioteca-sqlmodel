from datetime import date, timedelta
from typing import Optional
from fastapi import HTTPException, status
from sqlmodel import Session

from models.entities import Prestamo, PrestamoCreate
from repositories import libros as repo_libros
from repositories import prestamos as repo_prestamos
from repositories import socios as repo_socios


def registrar_prestamo(
    session: Session,
    datos: PrestamoCreate,
    fecha_hoy: Optional[date] = None,
) -> Prestamo:
    hoy = fecha_hoy if fecha_hoy is not None else date.today()

    # Regla 7: Recurso inexistente (Socio)
    socio = repo_socios.get_by_id(session, datos.socio_id)
    if not socio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Socio con id {datos.socio_id} no encontrado",
        )

    # Regla 3: Un socio inactivo no puede pedir préstamos (403)
    if not socio.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El socio se encuentra inactivo y no puede solicitar préstamos",
        )

    # Regla 1: Un socio no puede tener más de 3 préstamos activos (409)
    prestamos_activos = repo_prestamos.get_activos_by_socio(session, datos.socio_id)
    if len(prestamos_activos) >= 3:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El socio ya tiene el límite máximo de 3 préstamos activos",
        )

    # Regla 7: Recurso inexistente (Libro)
    libro = repo_libros.get_by_id(session, datos.libro_id)
    if not libro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Libro con id {datos.libro_id} no encontrado",
        )

    # Regla 2: No se presta un libro sin stock; al prestar se descuenta 1 (409)
    if libro.stock <= 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El libro '{libro.titulo}' no tiene stock disponible para préstamo",
        )

    # Regla 4: El plazo es de 14 días (fecha_vencimiento = fecha_prestamo + 14 días)
    vencimiento = hoy + timedelta(days=14)

    # Descontar stock usando repo_libros
    libro.stock -= 1
    repo_libros.save(session, libro)

    return repo_prestamos.create(
        session=session,
        socio_id=datos.socio_id,
        libro_id=datos.libro_id,
        fecha_prestamo=hoy,
        fecha_vencimiento=vencimiento,
    )


def registrar_devolucion(
    session: Session,
    prestamo_id: int,
    fecha_hoy: Optional[date] = None,
) -> Prestamo:
    hoy = fecha_hoy if fecha_hoy is not None else date.today()

    # Regla 7: Recurso inexistente (Préstamo)
    prestamo = repo_prestamos.get_by_id(session, prestamo_id)
    if not prestamo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Préstamo con id {prestamo_id} no encontrado",
        )

    # Regla 6: No se puede devolver un préstamo ya devuelto (409)
    if prestamo.fecha_devolucion is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El préstamo ya fue devuelto anteriormente",
        )

    # Regla 5: Al devolver se repone el stock y se calcula la multa:
    # $100 por día de atraso (0 si llegó a tiempo)
    dias_atraso = (hoy - prestamo.fecha_vencimiento).days
    if dias_atraso > 0:
        multa = float(dias_atraso * 100)
    else:
        multa = 0.0

    prestamo.fecha_devolucion = hoy
    prestamo.multa = multa

    # Reponer stock del libro
    libro = repo_libros.get_by_id(session, prestamo.libro_id)
    if libro:
        libro.stock += 1
        repo_libros.save(session, libro)

    return repo_prestamos.save(session, prestamo)
