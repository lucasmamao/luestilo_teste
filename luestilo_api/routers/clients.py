from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from luestilo_api.database import get_session
from luestilo_api.models import Client
from luestilo_api.schemas import ClientList, ClientPublic, ClientSchema, Message

router = APIRouter(prefix='/clients', tags=['clients'])


@router.post('/', status_code=HTTPStatus.CREATED, response_model=ClientPublic)
def create_client(
    client: ClientSchema, session: Session = Depends(get_session)
):
    db_client = session.scalar(
        select(Client).where(
            (Client.cpf == client.cpf) | (Client.email == client.email)
        )
    )

    if db_client:
        if db_client.cpf == client.cpf:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='CPF already exists',
            )
        elif db_client.email == client.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email already exists',
            )

    db_client = Client(name=client.name, cpf=client.cpf, email=client.email)
    session.add(db_client)
    session.commit()
    session.refresh(db_client)
    return db_client


@router.get('/', status_code=HTTPStatus.OK, response_model=ClientList)
def read_all_clients(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = Query(None, description="Filtrar por nome do cliente (parcial, case-insensitive)"),
    email: Optional[str] = Query(None, description="Filtrar por e-mail do cliente (parcial, case-insensitive)"),
    session: Session = Depends(get_session)
):
    query = select(Client).where(Client.is_active == True)

    if name:
        query = query.where(Client.name.ilike(f'%{name}%'))

    if email:
        query = query.where(Client.email.ilike(f'%{email}%'))

    query = query.offset(skip).limit(limit)

    clients = session.scalars(query).all()

    return {'clients': clients}


@router.get(
    '/{client_id}',
    status_code=HTTPStatus.OK,
    response_model=ClientPublic,
)
def read_client(client_id: int, session: Session = Depends(get_session)):
    db_client = session.scalar(select(Client).where(Client.id == client_id))
    if not db_client:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Client not found'
        )
    return db_client


@router.put(
    '/{client_id}',
    status_code=HTTPStatus.OK,
    response_model=ClientPublic,
)
def update_client(
    client_id: int,
    client: ClientSchema,
    session: Session = Depends(get_session),
):
    db_client = session.scalar(select(Client).where(Client.id == client_id))
    if not db_client:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Client not found'
        )

    db_client.name = client.name
    db_client.cpf = client.cpf
    db_client.email = client.email
    session.commit()
    session.refresh(db_client)

    return db_client


@router.delete(
    '/{client_id}',
    status_code=HTTPStatus.OK,
    response_model=Message,
)
def delete_client(client_id: int, session: Session = Depends(get_session)):
    db_client = session.scalar(select(Client).where(Client.id == client_id))

    if not db_client:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Client not found'
        )

    db_client.is_active = False
    session.add(db_client)

    session.commit()
    return {'message': 'Client deleted'}
