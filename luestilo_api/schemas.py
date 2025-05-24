from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, HttpUrl
from pydantic_br import CPF


class Message(BaseModel):
    message: str


class ClientSchema(BaseModel):
    name: str
    cpf: CPF
    email: EmailStr


class ClientPublic(BaseModel):
    id: int
    name: str
    cpf: CPF
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class ClientList(BaseModel):
    clients: list[ClientPublic]


class ProductSchema(BaseModel):
    descricao: str
    valor_de_venda: float
    codigo_de_barras: str
    secao: str
    estoque_inicial: int
    data_de_validade: Optional[date]
    imagens: list[HttpUrl]


class ProductPublic(BaseModel):
    descricao: str
    valor_de_venda: float
    codigo_de_barras: str
    secao: str
    estoque_inicial: int
    data_de_validade: Optional[date]
    imagens: list[HttpUrl]
    id: int


class ProductDB(ProductSchema):
    id: int


class ProductList(BaseModel):
    products: list[ProductPublic]


class OrderSchema(BaseModel):
    data_pedido: date
    secoes: list[str]
    status: str
    client_id: int


class OrderPublic(BaseModel):
    data_pedido: date
    secoes: list[str]
    status: str
    client_id: int
    id: int


class OrderDB(OrderSchema):
    id: int


class OrderList(BaseModel):
    orders: list[OrderPublic]
