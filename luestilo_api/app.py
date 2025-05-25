from fastapi import FastAPI
from http import HTTPStatus

from luestilo_api.routers import clients, products, orders, auth 
from luestilo_api.schemas import Message

app = FastAPI()

app.include_router(clients.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(auth.router) 

@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Olá Mundo!'}