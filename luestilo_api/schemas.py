from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field
from pydantic_br import CPF


class Message(BaseModel):
    message: str


class ClientSchema(BaseModel):
    name: str
    cpf: CPF
    email: EmailStr


class ClientPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    cpf: str
    email: EmailStr
    is_active: bool


class ClientList(BaseModel):
    clients: List[ClientPublic]


class ProductSchema(BaseModel):
    descricao: str
    valor_de_venda: float
    codigo_de_barras: str
    secao: str
    estoque_inicial: int
    data_validade: Optional[date] = None
    imagens: Optional[List[str]] = None


class ProductPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    descricao: str
    valor_de_venda: float
    codigo_de_barras: str
    secao: str
    estoque_inicial: int
    data_validade: Optional[date] = None
    imagens: Optional[List[str]] = None
    is_active: bool


class ProductList(BaseModel):
    products: List[ProductPublic]


class OrderProductSchema(BaseModel):
    product_id: int
    quantity: int
    price_at_order: Optional[float] = None


class OrderCreateSchema(BaseModel):
    client_id: int
    status: str
    periodo: date
    items: List[OrderProductSchema]


class OrderItemPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    product_id: int
    quantity: int
    price_at_order: float
    product: ProductPublic


class OrderPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: str
    periodo: date
    client_id: int
    is_active: bool
    products: List[OrderItemPublic]


class OrderList(BaseModel):
    orders: List[OrderPublic]


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: EmailStr


class UserList(BaseModel):
    users: List[UserPublic]


class CurrentUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class ClientFilterParams(BaseModel):
    skip: int = Field(0, description="Número de itens a pular (offset).")
    limit: int = Field(100, description="Número máximo de itens a retornar.")
    name: Optional[str] = Field(None, description="Filtrar por nome do cliente (parcial, case-insensitive).")
    email: Optional[EmailStr] = Field(None, description="Filtrar por e-mail do cliente (parcial, case-insensitive).")


class ProductFilterParams(BaseModel):
    skip: int = Field(0, description="Número de itens a pular (offset).")
    limit: int = Field(100, description="Número máximo de itens a retornar.")
    secao: Optional[str] = Field(None, description="Filtrar por seção do produto (parcial, case-insensitive).")
    min_price: Optional[float] = Field(None, description="Filtrar produtos com preço de venda a partir deste valor.")
    max_price: Optional[float] = Field(None, description="Filtrar produtos com preço de venda até este valor.")
    available: Optional[bool] = Field(None, description="Filtrar produtos disponíveis em estoque (True para >0, False para <=0).")


class OrderFilterParams(BaseModel):
    skip: int = Field(0, description="Número de itens a pular (offset).")
    limit: int = Field(100, description="Número máximo de itens a retornar.")
    start_periodo: Optional[date] = Field(None, description="Filtrar pedidos a partir desta data (YYYY-MM-DD).")
    end_periodo: Optional[date] = Field(None, description="Filtrar pedidos até esta data (YYYY-MM-DD).")
    product_section: Optional[str] = Field(None, description="Filtrar pedidos que contenham produtos de uma seção específica (parcial, case-insensitive).")
    status: Optional[str] = Field(None, description="Filtrar por status do pedido (exato, case-insensitive).")
    client_id: Optional[int] = Field(None, description="Filtrar por ID do cliente.")
