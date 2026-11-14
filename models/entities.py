from datetime import date
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel


# ==========================================
# 1. Tabla Intermedia N-N Libro <-> Autor
# ==========================================
class LibroAutor(SQLModel, table=True):
    libro_id: int | None = Field(default=None, foreign_key="libro.id", primary_key=True)
    autor_id: int | None = Field(default=None, foreign_key="autor.id", primary_key=True)


# ==========================================
# 2. Entidad Autor
# ==========================================
class AutorBase(SQLModel):
    nombre: str = Field(index=True)
    nacionalidad: str


class AutorCreate(AutorBase):
    pass


class AutorUpdate(SQLModel):
    nombre: Optional[str] = None
    nacionalidad: Optional[str] = None


class Autor(AutorBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    libros: list["Libro"] = Relationship(back_populates="autores", link_model=LibroAutor)


class AutorRead(AutorBase):
    id: int


# ==========================================
# 3. Entidad Libro
# ==========================================
class LibroBase(SQLModel):
    titulo: str = Field(index=True)
    isbn: str = Field(unique=True, index=True)
    stock: int = Field(default=0, ge=0)
    anio: int


class LibroCreate(LibroBase):
    pass


class LibroUpdate(SQLModel):
    titulo: Optional[str] = None
    isbn: Optional[str] = None
    stock: Optional[int] = Field(default=None, ge=0)
    anio: Optional[int] = None


class Libro(LibroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    autores: list[Autor] = Relationship(back_populates="libros", link_model=LibroAutor)
    prestamos: list["Prestamo"] = Relationship(back_populates="libro")


class LibroRead(LibroBase):
    id: int


class LibroReadWithAutores(LibroRead):
    autores: list[AutorRead] = []


# ==========================================
# 4. Entidad Socio
# ==========================================
class SocioBase(SQLModel):
    nombre: str
    email: str = Field(unique=True, index=True)
    activo: bool = True


class SocioCreate(SocioBase):
    pass


class SocioUpdate(SQLModel):
    nombre: Optional[str] = None
    email: Optional[str] = None
    activo: Optional[bool] = None


class Socio(SocioBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    prestamos: list["Prestamo"] = Relationship(back_populates="socio")


class SocioRead(SocioBase):
    id: int


# ==========================================
# 5. Entidad Préstamo
# ==========================================
class PrestamoBase(SQLModel):
    socio_id: int = Field(foreign_key="socio.id")
    libro_id: int = Field(foreign_key="libro.id")
    fecha_prestamo: date = Field(default_factory=date.today)
    fecha_vencimiento: date
    fecha_devolucion: Optional[date] = None
    multa: float = 0.0


class PrestamoCreate(SQLModel):
    socio_id: int
    libro_id: int


class Prestamo(PrestamoBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    socio: Optional[Socio] = Relationship(back_populates="prestamos")
    libro: Optional[Libro] = Relationship(back_populates="prestamos")


class PrestamoRead(PrestamoBase):
    id: int
