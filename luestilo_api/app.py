from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from luestilo_api.database import get_session
from luestilo_api.models import Client
from luestilo_api.schemas import (
    ClientList,
    ClientPublic,
    ClientSchema,
    Message,
    OrderDB,
    OrderList,
    OrderPublic,
    OrderSchema,
    ProductDB,
    ProductList,
    ProductPublic,
    ProductSchema,
)

app = FastAPI()
client_database = []
product_database = []
order_database = []


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Olá Mundo!'}


@app.post(
    '/clients/', status_code=HTTPStatus.CREATED, response_model=ClientPublic
)
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


@app.get('/clients/', status_code=HTTPStatus.OK, response_model=ClientList)
def read_all_clients(
    skip: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    clients = session.scalars(select(Client).offset(skip).limit(limit)).all()
    return {'clients': clients}


@app.get(
    '/clients/{client_id}',
    status_code=HTTPStatus.OK,
    response_model=ClientPublic,
)
def read_client(client_id: int):
    return client_database[client_id - 1]


@app.put(
    '/clients/{client_id}',
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


@app.delete(
    '/client/{client_id}',
    status_code=HTTPStatus.OK,
    response_model=Message,
)
def delete_client(client_id: int, session: Session = Depends(get_session)):
    db_client = session.scalar(select(Client).where(Client.id == client_id))

    if not db_client:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Client not found'
        )

    session.delete(db_client)

    session.commit()
    return {'message': 'Client deleted'}


@app.post(
    '/products/', status_code=HTTPStatus.CREATED, response_model=ProductPublic
)
def create_product(product: ProductSchema):
    product_with_id = ProductDB(
        **product.model_dump(), id=len(product_database) + 1
    )
    product_database.append(product_with_id)
    return product_with_id


@app.get('/products/', status_code=HTTPStatus.OK, response_model=ProductList)
def read_all_products():
    return {'products': product_database}


@app.get(
    '/products/{product_id}',
    status_code=HTTPStatus.OK,
    response_model=ProductPublic,
)
def read_product(product_id: int):
    return product_database[product_id - 1]


@app.put(
    '/products/{product_id}',
    status_code=HTTPStatus.OK,
    response_model=ProductPublic,
)
def update_product(product_id: int, product: ProductSchema):
    product_with_id = ProductDB(**product.model_dump(), id=product_id)
    product_database[product_id - 1] = product_with_id

    return product_with_id


@app.delete(
    '/products/{product_id}',
    status_code=HTTPStatus.OK,
    response_model=ProductPublic,
)
def delete_product(product_id: int):
    return product_database.pop(product_id - 1)


@app.post(
    '/orders/', status_code=HTTPStatus.CREATED, response_model=OrderPublic
)
def create_order(order: OrderSchema):
    order_with_id = OrderDB(**order.model_dump(), id=len(order_database) + 1)
    order_database.append(order_with_id)
    return order_with_id


@app.get('/orders/', status_code=HTTPStatus.OK, response_model=OrderList)
def read_all_orders():
    return {'orders': order_database}


@app.get(
    '/orders/{order_id}',
    status_code=HTTPStatus.OK,
    response_model=OrderPublic,
)
def read_order(order_id: int):
    return order_database[order_id - 1]


@app.put(
    '/orders/{order_id}',
    status_code=HTTPStatus.OK,
    response_model=OrderPublic,
)
def update_order(order_id: int, order: OrderSchema):
    order_with_id = OrderDB(**order.model_dump(), id=order_id)
    order_database[order_id - 1] = order_with_id

    return order_with_id


@app.delete(
    '/orders/{order_id}',
    status_code=HTTPStatus.OK,
    response_model=OrderPublic,
)
def delete_order(order_id: int):
    return order_database.pop(order_id - 1)
