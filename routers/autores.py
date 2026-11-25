from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from models.entities import Autor, AutorCreate, AutorRead, AutorUpdate
from repositories.database import get_session
from services import autores as service_autores

router = APIRouter(prefix="/autores", tags=["Autores"])


@router.post("", response_model=AutorRead, status_code=status.HTTP_201_CREATED)
def crear_autor(autor: AutorCreate, session: Session = Depends(get_session)) -> Autor:
    return service_autores.create_autor(session, autor)


@router.get("", response_model=list[AutorRead])
def listar_autores(session: Session = Depends(get_session)) -> list[Autor]:
    return list(service_autores.get_autores(session))


@router.get("/{id}", response_model=AutorRead)
def obtener_autor(id: int, session: Session = Depends(get_session)) -> Autor:
    return service_autores.get_autor_by_id(session, id)


@router.put("/{id}", response_model=AutorRead)
def actualizar_autor(
    id: int, autor_update: AutorUpdate, session: Session = Depends(get_session)
) -> Autor:
    return service_autores.update_autor(session, id, autor_update)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_autor(id: int, session: Session = Depends(get_session)) -> None:
    service_autores.delete_autor(session, id)
    return None
