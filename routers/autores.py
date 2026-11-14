from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from models.entities import Autor, AutorCreate, AutorRead, AutorUpdate
from repositories.database import get_session

router = APIRouter(prefix="/autores", tags=["Autores"])


@router.post("", response_model=AutorRead, status_code=status.HTTP_201_CREATED)
def crear_autor(autor: AutorCreate, session: Session = Depends(get_session)) -> Autor:
    db_autor = Autor.model_validate(autor)
    session.add(db_autor)
    session.commit()
    session.refresh(db_autor)
    return db_autor


@router.get("", response_model=list[AutorRead])
def listar_autores(session: Session = Depends(get_session)) -> list[Autor]:
    autores = session.exec(select(Autor)).all()
    return list(autores)


@router.get("/{id}", response_model=AutorRead)
def obtener_autor(id: int, session: Session = Depends(get_session)) -> Autor:
    autor = session.get(Autor, id)
    if not autor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Autor con id {id} no encontrado",
        )
    return autor


@router.put("/{id}", response_model=AutorRead)
def actualizar_autor(
    id: int, autor_update: AutorUpdate, session: Session = Depends(get_session)
) -> Autor:
    autor = session.get(Autor, id)
    if not autor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Autor con id {id} no encontrado",
        )
    update_data = autor_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(autor, key, value)
    session.add(autor)
    session.commit()
    session.refresh(autor)
    return autor


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_autor(id: int, session: Session = Depends(get_session)):
    autor = session.get(Autor, id)
    if not autor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Autor con id {id} no encontrado",
        )
    session.delete(autor)
    session.commit()
    return None
