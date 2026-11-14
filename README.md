# TP: Sistema de Gestión de Biblioteca (FastAPI + SQLModel)

API REST para la gestión del catálogo de una biblioteca y sus préstamos, construida con **FastAPI** y **SQLModel (SQLite)** cumpliendo arquitectura por capas y reglas de negocio con códigos HTTP estándar.

---

## 🏛️ Estructura del Proyecto

```
tp-biblioteca-sqlmodel/
├── main.py                     # Punto de entrada de la aplicación FastAPI y lifespan
├── models/
│   ├── __init__.py
│   └── entities.py             # Modelos SQLModel (Autor, Libro, LibroAutor N-N, Socio, Prestamo)
├── routers/
│   ├── __init__.py
│   ├── autores.py              # Endpoints CRUD para /autores
│   ├── libros.py               # Endpoints CRUD, filtro disponibles y relación N-N con autores
│   ├── socios.py               # Endpoints CRUD y consulta de préstamos por socio
│   └── prestamos.py            # Endpoints para registro y devolución de préstamos
├── services/
│   ├── __init__.py
│   └── prestamos.py            # Lógica de negocio (reglas de préstamo, stock, cálculo de multas)
├── repositories/
│   ├── __init__.py
│   └── database.py             # Configuración del engine SQLite y generador de sesiones
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Fixtures de pytest con base de datos SQLite en memoria
│   ├── test_crud.py            # Tests de CRUD, relaciones N-N y validaciones
│   └── test_prestamos.py       # Tests de reglas de negocio, límites, stock y multas
├── requirements.txt            # Dependencias del proyecto
└── README.md
```

---

## ⚙️ Requisitos e Instalación

### 1. Crear el entorno virtual (`venv`)

Desde la raíz del proyecto (`tp-biblioteca-sqlmodel`):

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

## 🧪 Ejecutar los Tests y Cobertura

Para correr los tests unitarios y de integración con base de datos SQLite en memoria:

```bash
pytest
```

Para correr los tests con reporte de cobertura:

```bash
pytest --cov=models --cov=routers --cov=services --cov-report=term-missing
```

---

## 📋 Reglas de Negocio Implementadas

| # | Regla | Código HTTP |
|---|---|---|
| **1** | Un socio no puede tener más de 3 préstamos activos simultáneamente | `409 Conflict` |
| **2** | No se presta un libro sin stock (`stock <= 0`); al prestar se descuenta 1 unidad | `409 Conflict` |
| **3** | Un socio inactivo (`activo == False`) no puede pedir préstamos | `403 Forbidden` |
| **4** | El plazo es de 14 días (`fecha_vencimiento = fecha_prestamo + 14 días`) | N/A |
| **5** | Al devolver se repone el stock y se calcula la multa: **$100 × días de atraso** (0 si llegó a tiempo) | N/A |
| **6** | No se puede devolver un préstamo ya devuelto | `409 Conflict` |
| **7** | Recurso inexistente (autor, libro, socio, préstamo) | `404 Not Found` |
| **8** | ISBN de libro duplicado o Email de socio duplicado | `409 Conflict` |
