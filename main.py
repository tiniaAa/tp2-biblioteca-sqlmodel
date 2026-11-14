from contextlib import asynccontextmanager
from fastapi import FastAPI

from repositories.database import create_db_and_tables
from routers import autores, libros, prestamos, socios


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="Sistema de Biblioteca",
    description="API REST para gestionar catálogo y préstamos de biblioteca con FastAPI y SQLModel.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(autores.router)
app.include_router(libros.router)
app.include_router(socios.router)
app.include_router(prestamos.router)


@app.get("/")
def read_root():
    return {
        "message": "Bienvenido al Sistema de Gestión de Biblioteca",
        "docs": "/docs",
    }
