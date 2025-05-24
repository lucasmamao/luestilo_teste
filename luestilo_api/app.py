from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from luestilo_api.database import get_session
from luestilo_api.models import Client, Order, OrderProduct, Product, User
from luestilo_api.schemas import (
    ClientList,
    ClientPublic,
    ClientSchema,
    Message,
    OrderCreateSchema,
    OrderList,
    OrderPublic,
    ProductList,
    ProductPublic,
    ProductSchema,
    Token,
    UserPublic,
    UserSchema,
)
from luestilo_api.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)

app = FastAPI()


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
def read_client(client_id: int, session: Session = Depends(get_session)):
    db_client = session.scalar(select(Client).where(Client.id == client_id))
    if not db_client:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Client not found'
        )
    return db_client


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
    '/clients/{client_id}',
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


@app.post('/products/', status_code=HTTPStatus.CREATED, response_model=ProductPublic)
def create_product(product: ProductSchema, session: Session = Depends(get_session)):
    db_product = session.scalar(
        select(Product).where(Product.codigo_de_barras == product.codigo_de_barras)
    )
    if db_product:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Product with this barcode already exists',
        )

    db_product = Product(**product.model_dump())
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product


@app.get('/products/', status_code=HTTPStatus.OK, response_model=ProductList)
def read_all_products(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    products = session.scalars(select(Product).offset(skip).limit(limit)).all()
    return {'products': products}


@app.get('/products/{product_id}', status_code=HTTPStatus.OK, response_model=ProductPublic)
def read_product(product_id: int, session: Session = Depends(get_session)):
    db_product = session.scalar(select(Product).where(Product.id == product_id))
    if not db_product:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Product not found'
        )
    return db_product


@app.put('/products/{product_id}', status_code=HTTPStatus.OK, response_model=ProductPublic)
def update_product(product_id: int,
    product: ProductSchema,
    session: Session = Depends(get_session)
):
    db_product = session.scalar(select(Product).where(Product.id == product_id))
    if not db_product:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Product not found'
        )

    if db_product.codigo_de_barras != product.codigo_de_barras:
        existing_product = session.scalar(
            select(Product).where(
                (Product.id != product_id) &
                (Product.codigo_de_barras == product.codigo_de_barras)
            )
        )
        if existing_product:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Product with this barcode already exists for another product',
            )

    for key, value in product.model_dump(exclude_unset=True).items():
        setattr(db_product, key, value)

    session.commit()
    session.refresh(db_product)
    return db_product


@app.delete('/products/{product_id}', status_code=HTTPStatus.OK, response_model=Message)
def delete_product(product_id: int, session: Session = Depends(get_session)):
    db_product = session.scalar(select(Product).where(Product.id == product_id))
    if not db_product:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Product not found'
        )
    session.delete(db_product)
    session.commit()
    return {'message': 'Product deleted'}


@app.post('/orders/', status_code=HTTPStatus.CREATED, response_model=OrderPublic)
def create_order(order_data: OrderCreateSchema, session: Session = Depends(get_session)):
    db_client = session.scalar(select(Client).where(Client.id == order_data.client_id))
    if not db_client:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Client not found'
        )

    db_order = Order(
        client_id=order_data.client_id,
        status=order_data.status,
        periodo=order_data.periodo
    )
    session.add(db_order)
    session.flush()

    for item_data in order_data.items:
        db_product = session.scalar(select(Product).where(Product.id == item_data.product_id))
        if not db_product:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f'Product with ID {item_data.product_id} not found',
            )

        price_to_use = item_data.price_at_order if item_data.price_at_order is not None else db_product.valor_de_venda

        db_order_product = OrderProduct(
            order_id=db_order.id,
            product_id=db_product.id,
            quantity=item_data.quantity,
            price_at_order=price_to_use
        )
        session.add(db_order_product)

    session.commit()
    session.refresh(db_order)
    return db_order


@app.get('/orders/', status_code=HTTPStatus.OK, response_model=OrderList)
def read_all_orders(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    orders = session.scalars(
        select(Order)
        .options(joinedload(Order.products).joinedload(OrderProduct.product))
        .offset(skip).limit(limit)
    ).all()
    return {'orders': orders}


@app.get('/orders/{order_id}', status_code=HTTPStatus.OK, response_model=OrderPublic)
def read_order(order_id: int, session: Session = Depends(get_session)):
    db_order = session.scalar(
        select(Order)
        .where(Order.id == order_id)
        .options(joinedload(Order.products).joinedload(OrderProduct.product))
    )
    if not db_order:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Order not found'
        )
    return db_order


@app.put('/orders/{order_id}', status_code=HTTPStatus.OK, response_model=OrderPublic)
def update_order(
    order_id: int,
    order_update_data: OrderCreateSchema,
    session: Session = Depends(get_session)
):
    db_order = session.scalar(select(Order).where(Order.id == order_id))
    if not db_order:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Order not found'
        )

    db_order.status = order_update_data.status
    db_order.periodo = order_update_data.periodo

    session.commit()
    session.refresh(db_order)
    return db_order


@app.delete('/orders/{order_id}', status_code=HTTPStatus.OK, response_model=Message)
def delete_order(order_id: int, session: Session = Depends(get_session)):
    db_order = session.scalar(select(Order).where(Order.id == order_id))
    if not db_order:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Order not found'
        )
    session.delete(db_order)
    session.commit()
    return {'message': 'Order deleted'}


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: Session = Depends(get_session)):
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username already exists',
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email already exists',
            )

    hashed_password = get_password_hash(user.password)

    db_user = User(
        email=user.email,
        username=user.username,
        password=hashed_password,
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@app.post('/token', response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),


    session: Session = Depends(get_session),
):
    user = session.scalar(select(User).where(User.email == form_data.username))

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password'
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password'
        )

    access_token = create_access_token(data={'sub': user.email})

    return {'access_token': access_token, 'token_type': 'bearer'}
