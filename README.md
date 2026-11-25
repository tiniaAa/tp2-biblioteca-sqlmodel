# TP: Sistema de Gestión de Biblioteca (FastAPI + SQLModel)

API REST para la gestión del catálogo de una biblioteca y sus préstamos, construida con **FastAPI** y **SQLModel (SQLite)** cumpliendo estrictamente con una **arquitectura por capas desacoplada** (`routers` -> `services` -> `repositories` -> `database`).

---

## 🏛️ Estructura del Proyecto por Capas

```
tp2-biblioteca-sqlmodel/
├── main.py                     # Instancia de FastAPI y lifespan (creación de tablas SQLite)
├── models/
│   ├── __init__.py
│   └── entities.py             # Modelos SQLModel (Autor, Libro, LibroAutor N-N, Socio, Prestamo)
├── repositories/               # Capa de ACCESO A DATOS (Consultas SQLModel puras)
│   ├── __init__.py
│   ├── database.py             # Configuración del engine SQLite (biblioteca.db) y sesiones
│   ├── autores.py              # Queries y operaciones CRUD en BD para Autor
│   ├── libros.py               # Queries en BD para Libro, stock y relación N-N con Autor
│   ├── socios.py               # Queries en BD para Socio y búsquedas por email
│   └── prestamos.py            # Queries en BD para Prestamo y préstamos activos
├── services/                   # Capa de LÓGICA DE NEGOCIO (Reglas, validaciones y códigos HTTP)
│   ├── __init__.py
│   ├── autores.py              # Lógica y validaciones de autores
│   ├── libros.py               # Lógica de libros y validación de ISBN único (409)
│   ├── socios.py               # Lógica de socios y validación de email único (409)
│   └── prestamos.py            # Orquestación de préstamos, límite de 3, stock y multas
├── routers/                    # Capa de CONTROLADORES / API REST (Rutas y status codes)
│   ├── __init__.py
│   ├── autores.py              # Endpoints para /autores
│   ├── libros.py               # Endpoints para /libros y /libros/{id}/autores/{autor_id}
│   ├── socios.py               # Endpoints para /socios y /socios/{id}/prestamos
│   └── prestamos.py            # Endpoints para /prestamos y /prestamos/{id}/devolucion
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Fixtures con base SQLite en memoria (StaticPool)
│   ├── test_crud.py            # Tests de CRUDs, ISBN único, email único y relación N-N
│   └── test_prestamos.py       # Tests de las 8 reglas de negocio (casos exitosos y errores)
├── requirements.txt
└── README.md
```

---

## ⚙️ Requisitos e Instalación

### 1. Crear y activar el entorno virtual (`venv`)

```bash
python -m venv .venv
```

Activar el entorno:
- **Windows (PowerShell):**
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
- **macOS / Linux:**
  ```bash
  source .venv/bin/activate
  ```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 🚀 Ejecutar la Aplicación

Con el entorno virtual activado:

```bash
uvicorn main:app --reload
```

- **API URL:** `http://127.0.0.1:8000`
- **Documentación Interactiva (Swagger UI):** `http://127.0.0.1:8000/docs`

---

## 🧪 Ejecutar Tests con Cobertura (≥ 90%)

Para correr los tests y verificar la cobertura de todas las capas:

```bash
pytest -v --cov=models --cov=routers --cov=services --cov=repositories --cov-report=term-missing
```

---

## 📋 Reglas de Negocio Implementadas

| # | Regla | Código HTTP | Capa que la valida |
|---|---|---|---|
| **1** | Máximo 3 préstamos activos por socio simultáneamente | `409 Conflict` | `services/prestamos.py` |
| **2** | No prestar libro sin stock (`stock <= 0`); descuenta 1 al prestar | `409 Conflict` | `services/prestamos.py` |
| **3** | Socio inactivo (`activo == False`) no puede pedir préstamos | `403 Forbidden` | `services/prestamos.py` |
| **4** | Plazo de 14 días (`fecha_vencimiento = fecha_prestamo + 14 días`) | N/A | `services/prestamos.py` |
| **5** | Al devolver repone stock y calcula multa: **$100 × días de atraso** (0 a tiempo) | N/A | `services/prestamos.py` |
| **6** | No devolver un préstamo ya devuelto | `409 Conflict` | `services/prestamos.py` |
| **7** | Recurso inexistente (autor, libro, socio, préstamo) | `404 Not Found` | `services/*.py` |
| **8** | ISBN de libro duplicado o Email de socio duplicado | `409 Conflict` | `services/libros.py` / `services/socios.py` |
