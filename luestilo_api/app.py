from http import HTTPStatus

from fastapi import FastAPI

from luestilo_api.schemas import (
    ClientDB,
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
def create_client(client: ClientSchema):
    client_with_id = ClientDB(
        **client.model_dump(), id=len(client_database) + 1
    )
    client_database.append(client_with_id)
    return client_with_id


@app.get('/clients/', status_code=HTTPStatus.OK, response_model=ClientList)
def read_all_clients():
    return {'clients': client_database}


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
def update_client(client_id: int, client: ClientSchema):
    client_with_id = ClientDB(**client.model_dump(), id=client_id)
    client_database[client_id - 1] = client_with_id

    return client_with_id


@app.delete(
    '/client/{client_id}',
    status_code=HTTPStatus.OK,
    response_model=ClientPublic,
)
def delete_client(client_id: int):
    return client_database.pop(client_id - 1)


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
