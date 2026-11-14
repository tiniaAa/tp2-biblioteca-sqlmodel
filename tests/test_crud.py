from fastapi.testclient import TestClient


def test_crud_autor(client: TestClient):
    # Create
    res = client.post("/autores", json={"nombre": "Jorge Luis Borges", "nacionalidad": "Argentina"})
    assert res.status_code == 201
    data = res.json()
    autor_id = data["id"]
    assert data["nombre"] == "Jorge Luis Borges"

    # Read All
    res_list = client.get("/autores")
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 1

    # Read By ID
    res_one = client.get(f"/autores/{autor_id}")
    assert res_one.status_code == 200
    assert res_one.json()["nombre"] == "Jorge Luis Borges"

    # Update
    res_up = client.put(f"/autores/{autor_id}", json={"nombre": "J. L. Borges"})
    assert res_up.status_code == 200
    assert res_up.json()["nombre"] == "J. L. Borges"

    # Delete
    res_del = client.delete(f"/autores/{autor_id}")
    assert res_del.status_code == 204

    # 404 after delete
    res_404 = client.get(f"/autores/{autor_id}")
    assert res_404.status_code == 404


def test_crud_libro_y_filtro_disponibles(client: TestClient):
    # Create libro con stock > 0
    res1 = client.post("/libros", json={"titulo": "Ficciones", "isbn": "978-987-566-648-1", "stock": 2, "anio": 1944})
    assert res1.status_code == 201
    libro1_id = res1.json()["id"]

    # Create libro sin stock
    res2 = client.post("/libros", json={"titulo": "El Aleph", "isbn": "978-987-566-649-8", "stock": 0, "anio": 1949})
    assert res2.status_code == 201

    # Filtrar disponibles=true
    res_disp = client.get("/libros?disponibles=true")
    assert res_disp.status_code == 200
    titulos_disp = [l["titulo"] for l in res_disp.json()]
    assert "Ficciones" in titulos_disp
    assert "El Aleph" not in titulos_disp

    # Regla 8: ISBN duplicado -> 409
    res_dup = client.post("/libros", json={"titulo": "Otro Ficciones", "isbn": "978-987-566-648-1", "stock": 5, "anio": 2000})
    assert res_dup.status_code == 409

    # Update con ISBN duplicado de otro libro -> 409
    res_up_dup = client.put(f"/libros/{libro1_id}", json={"isbn": "978-987-566-649-8"})
    assert res_up_dup.status_code == 409


def test_relacion_libro_autor_nn(client: TestClient):
    # Crear autor
    res_a = client.post("/autores", json={"nombre": "Adolfo Bioy Casares", "nacionalidad": "Argentina"})
    autor_id = res_a.json()["id"]

    # Crear libro
    res_l = client.post("/libros", json={"titulo": "La invención de Morel", "isbn": "978-84-206-3311-4", "stock": 3, "anio": 1940})
    libro_id = res_l.json()["id"]

    # Asociar autor a libro
    res_asoc = client.post(f"/libros/{libro_id}/autores/{autor_id}")
    assert res_asoc.status_code == 200
    autores = res_asoc.json()["autores"]
    assert any(a["id"] == autor_id for a in autores)

    # Re-asociar (idempotente)
    res_asoc2 = client.post(f"/libros/{libro_id}/autores/{autor_id}")
    assert res_asoc2.status_code == 200

    # 404 al asociar autor o libro inexistente
    assert client.post(f"/libros/999/autores/{autor_id}").status_code == 404
    assert client.post(f"/libros/{libro_id}/autores/999").status_code == 404


def test_crud_socio_y_reglas(client: TestClient):
    # Create socio
    res = client.post("/socios", json={"nombre": "Lucas Torres", "email": "lucas@example.com", "activo": True})
    assert res.status_code == 201
    socio_id = res.json()["id"]

    # Regla 8: Email duplicado -> 409
    res_dup = client.post("/socios", json={"nombre": "Lucas Dos", "email": "lucas@example.com", "activo": True})
    assert res_dup.status_code == 409

    # Update email duplicado -> 409
    res2 = client.post("/socios", json={"nombre": "María Gómez", "email": "maria@example.com", "activo": True})
    socio2_id = res2.json()["id"]
    res_up_dup = client.put(f"/socios/{socio2_id}", json={"email": "lucas@example.com"})
    assert res_up_dup.status_code == 409

    # Delete socio
    assert client.delete(f"/socios/{socio2_id}").status_code == 204
    assert client.get(f"/socios/{socio2_id}").status_code == 404
