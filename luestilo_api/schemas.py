from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr
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
    data_validade: Optional[date] = None
    imagens: List[str] = []


class ProductPublic(ProductSchema):
    model_config = ConfigDict(from_attributes=True)
    id: int


class ProductDB(ProductSchema):
    id: int


class ProductList(BaseModel):
    products: list[ProductPublic]


class OrderProductSchema(BaseModel):
    product_id: int
    quantity: int
    price_at_order: Optional[float] = None


class OrderCreateSchema(BaseModel):
    client_id: int
    status: str
    periodo: date
    items: List[OrderProductSchema] = []


class ProductInOrder(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    descricao: str
    codigo_de_barras: str
    valor_de_venda: float


class OrderItemPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    product: ProductInOrder
    quantity: int
    price_at_order: float


class OrderPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: str
    periodo: date
    client_id: int
    products: List[OrderItemPublic] = []


class OrderList(BaseModel):
    orders: List[OrderPublic]
