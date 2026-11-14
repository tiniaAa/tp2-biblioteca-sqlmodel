from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from models.entities import (
    Autor,
    Libro,
    LibroAutor,
    LibroCreate,
    LibroRead,
    LibroReadWithAutores,
    LibroUpdate,
)
from repositories.database import get_session

router = APIRouter(prefix="/libros", tags=["Libros"])


@router.post("", response_model=LibroRead, status_code=status.HTTP_201_CREATED)
def crear_libro(libro: LibroCreate, session: Session = Depends(get_session)) -> Libro:
    # Regla 8: ISBN duplicado -> 409
    existente = session.exec(select(Libro).where(Libro.isbn == libro.isbn)).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un libro con el ISBN '{libro.isbn}'",
        )

    db_libro = Libro.model_validate(libro)
    session.add(db_libro)
    session.commit()
    session.refresh(db_libro)
    return db_libro


@router.get("", response_model=list[LibroReadWithAutores])
def listar_libros(
    disponibles: Optional[bool] = Query(
        default=None,
        description="Filtrar por libros con stock > 0 si es True",
    ),
    session: Session = Depends(get_session),
) -> list[Libro]:
    query = select(Libro)
    if disponibles is True:
        query = query.where(Libro.stock > 0)
    elif disponibles is False:
        query = query.where(Libro.stock == 0)
    libros = session.exec(query).all()
    return list(libros)


@router.get("/{id}", response_model=LibroReadWithAutores)
def obtener_libro(id: int, session: Session = Depends(get_session)) -> Libro:
    libro = session.get(Libro, id)
    if not libro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Libro con id {id} no encontrado",
        )
    return libro


@router.put("/{id}", response_model=LibroRead)
def actualizar_libro(
    id: int, libro_update: LibroUpdate, session: Session = Depends(get_session)
) -> Libro:
    libro = session.get(Libro, id)
    if not libro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Libro con id {id} no encontrado",
        )

    # Verificar si el nuevo ISBN choca con otro libro existente
    if libro_update.isbn is not None and libro_update.isbn != libro.isbn:
        duplicado = session.exec(
            select(Libro).where(Libro.isbn == libro_update.isbn, Libro.id != id)
        ).first()
        if duplicado:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe otro libro con el ISBN '{libro_update.isbn}'",
            )

    update_data = libro_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(libro, key, value)
    session.add(libro)
    session.commit()
    session.refresh(libro)
    return libro


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_libro(id: int, session: Session = Depends(get_session)):
    libro = session.get(Libro, id)
    if not libro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Libro con id {id} no encontrado",
        )
    session.delete(libro)
    session.commit()
    return None


@router.post(
    "/{id}/autores/{autor_id}",
    response_model=LibroReadWithAutores,
    status_code=status.HTTP_200_OK,
)
def asociar_autor_a_libro(
    id: int, autor_id: int, session: Session = Depends(get_session)
) -> Libro:
    # Regla 7: Recurso inexistente (Libro o Autor)
    libro = session.get(Libro, id)
    if not libro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Libro con id {id} no encontrado",
        )

    autor = session.get(Autor, autor_id)
    if not autor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Autor con id {autor_id} no encontrado",
        )

    # Verificar si ya está asociado
    asociacion = session.exec(
        select(LibroAutor).where(
            LibroAutor.libro_id == id,
            LibroAutor.autor_id == autor_id,
        )
    ).first()

    if not asociacion:
        nueva_asoc = LibroAutor(libro_id=id, autor_id=autor_id)
        session.add(nueva_asoc)
        session.commit()

    session.refresh(libro)
    return libro
