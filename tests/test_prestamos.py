from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlmodel import Session

from services.prestamos import registrar_devolucion, registrar_prestamo


def test_reglas_prestamo(client: TestClient, session: Session):
    # Setup Socio activo y Socio inactivo
    res_s1 = client.post("/socios", json={"nombre": "Ana Ramos", "email": "ana@test.com", "activo": True})
    s1_id = res_s1.json()["id"]

    res_s2 = client.post("/socios", json={"nombre": "Inactivo Juan", "email": "juan@test.com", "activo": False})
    s2_id = res_s2.json()["id"]

    # Setup Libros
    res_l1 = client.post("/libros", json={"titulo": "Libro 1", "isbn": "ISBN-001", "stock": 5, "anio": 2020})
    l1_id = res_l1.json()["id"]

    res_l2 = client.post("/libros", json={"titulo": "Libro Sin Stock", "isbn": "ISBN-002", "stock": 0, "anio": 2021})
    l2_id = res_l2.json()["id"]

    # Regla 7: Socio inexistente -> 404
    assert client.post("/prestamos", json={"socio_id": 9999, "libro_id": l1_id}).status_code == 404

    # Regla 7: Libro inexistente -> 404
    assert client.post("/prestamos", json={"socio_id": s1_id, "libro_id": 9999}).status_code == 404

    # Regla 3: Socio inactivo -> 403
    res_inactivo = client.post("/prestamos", json={"socio_id": s2_id, "libro_id": l1_id})
    assert res_inactivo.status_code == 403

    # Regla 2: Libro sin stock -> 409
    res_sin_stock = client.post("/prestamos", json={"socio_id": s1_id, "libro_id": l2_id})
    assert res_sin_stock.status_code == 409

    # Préstamo 1 exitoso -> Regla 4: fecha_vencimiento = fecha_prestamo + 14 días y descuento de stock
    res_p1 = client.post("/prestamos", json={"socio_id": s1_id, "libro_id": l1_id})
    assert res_p1.status_code == 201
    p1_data = res_p1.json()
    p1_id = p1_data["id"]

    f_prestamo = date.fromisoformat(p1_data["fecha_prestamo"])
    f_vencimiento = date.fromisoformat(p1_data["fecha_vencimiento"])
    assert (f_vencimiento - f_prestamo).days == 14

    # Verificar que el stock bajó a 4
    libro_check = client.get(f"/libros/{l1_id}").json()
    assert libro_check["stock"] == 4

    # Crear 2 préstamos más para alcanzar el límite de 3
    res_p2 = client.post("/prestamos", json={"socio_id": s1_id, "libro_id": l1_id})
    assert res_p2.status_code == 201
    res_p3 = client.post("/prestamos", json={"socio_id": s1_id, "libro_id": l1_id})
    assert res_p3.status_code == 201

    # Regla 1: Un socio no puede tener más de 3 préstamos activos -> 409
    res_p4 = client.post("/prestamos", json={"socio_id": s1_id, "libro_id": l1_id})
    assert res_p4.status_code == 409

    # Consultar préstamos activos del socio
    res_activos = client.get(f"/socios/{s1_id}/prestamos?activos=true")
    assert res_activos.status_code == 200
    assert len(res_activos.json()) == 3

    # Devolución a tiempo (multa = 0)
    res_dev = client.post(f"/prestamos/{p1_id}/devolucion")
    assert res_dev.status_code == 200
    dev_data = res_dev.json()
    assert dev_data["fecha_devolucion"] is not None
    assert dev_data["multa"] == 0.0

    # Stock recuperado
    assert client.get(f"/libros/{l1_id}").json()["stock"] == 3

    # Regla 6: Devolver préstamo ya devuelto -> 409
    assert client.post(f"/prestamos/{p1_id}/devolucion").status_code == 409

    # Devolución inexistente -> 404
    assert client.post("/prestamos/99999/devolucion").status_code == 404


def test_multa_con_atraso(session: Session):
    from models.entities import PrestamoCreate

    # Simulando préstamo con fecha pasada para verificar cálculo de multa ($100 x días)
    # Creamos socio y libro directamente
    from models.entities import Libro, Socio

    socio = Socio(nombre="Pedro", email="pedro@multa.com", activo=True)
    libro = Libro(titulo="Libro Multa", isbn="ISBN-MULTA", stock=1, anio=2022)
    session.add(socio)
    session.add(libro)
    session.commit()
    session.refresh(socio)
    session.refresh(libro)

    fecha_inicio = date(2026, 1, 1)
    prestamo = registrar_prestamo(
        session=session,
        datos=PrestamoCreate(socio_id=socio.id, libro_id=libro.id),
        fecha_hoy=fecha_inicio,
    )

    # Vencía el 15/01/2026. Si se devuelve el 20/01/2026 -> 5 días de atraso -> multa = $500
    fecha_entrega_tarde = date(2026, 1, 20)
    devuelto = registrar_devolucion(
        session=session,
        prestamo_id=prestamo.id,
        fecha_hoy=fecha_entrega_tarde,
    )

    assert devuelto.fecha_devolucion == fecha_entrega_tarde
    assert devuelto.multa == 500.0
    # Stock repuesto
    session.refresh(libro)
    assert libro.stock == 1
