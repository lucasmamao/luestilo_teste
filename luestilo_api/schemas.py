from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field
from pydantic_br import CPF


class Message(BaseModel):
    message: str


class ClientSchema(BaseModel):
    name: str = Field(..., example="Maria Silva")
    cpf: CPF
    email: EmailStr = Field(..., example="maria.silva@email.com")
    numero_whatsapp: Optional[str] = Field(
        None,
        pattern=r"^\+?[0-9]{10,15}$",
        example="+5535991234567"
    )
    aceita_notificacoes_whatsapp: bool = Field(
        False,
        example=True
    )

    model_config = ConfigDict(
    json_schema_extra={
        "example": { 
            "name": "CPF TEM QUE SER VALIDO DA SILVA",
            "cpf": "916.678.060-84", 
            "email": "cpf.valido@example.com",
            "numero_whatsapp": "+5511987654321",
            "aceita_notificacoes_whatsapp": True
        }
    }
    )


class ClientPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., example=1)
    name: str = Field(..., example="Maria Silva")
    cpf: str = Field(..., example="123.456.789-00") 
    email: EmailStr = Field(..., example="maria.silva@email.com")
    is_active: bool = Field(..., example=True)
    numero_whatsapp: Optional[str] = Field(None, example="+5535991234567")
    aceita_notificacoes_whatsapp: bool = Field(False, example=True)

class ClientList(BaseModel):
    clients: List[ClientPublic]


class ProductSchema(BaseModel):
    descricao: str = Field(..., example="Camiseta Algodão Branca M") 
    valor_de_venda: float = Field(..., example=59.99) 
    codigo_de_barras: str = Field(..., example="7891234567890") 
    secao: str = Field(..., example="Vestuário Feminino") 
    estoque_inicial: int = Field(..., example=100) 
    data_validade: Optional[date] = Field(None, example=date(2025, 12, 31)) 
    imagens: Optional[List[str]] = Field(None, example=["http://example.com/img1.jpg", "http://example.com/img2.png"]) 


class ProductPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., example=1)
    descricao: str = Field(..., example="Camiseta Algodão Branca M")
    valor_de_venda: float = Field(..., example=59.99)
    codigo_de_barras: str = Field(..., example="7891234567890")
    secao: str = Field(..., example="Vestuário Feminino")
    estoque_inicial: int = Field(..., example=100)
    data_validade: Optional[date] = Field(None, example=date(2025, 12, 31))
    imagens: Optional[List[str]] = Field(None, example=["http://example.com/img1.jpg", "http://example.com/img2.png"])
    is_active: bool = Field(..., example=True)


class ProductList(BaseModel):
    products: List[ProductPublic]


class OrderProductSchema(BaseModel):
    product_id: int = Field(..., example=1) 
    quantity: int = Field(..., example=2) 
    price_at_order: Optional[float] = Field(None, example=59.99) 


class OrderCreateSchema(BaseModel):
    client_id: int = Field(..., example=1) 
    status: str = Field(..., example="pendente") 
    periodo: date = Field(..., example=date(2025, 5, 26)) 
    items: List[OrderProductSchema] = Field(
        ...,
        examples=[ 
            [
                {"product_id": 1, "quantity": 1, "price_at_order": 59.99},
                {"product_id": 2, "quantity": 3, "price_at_order": 19.90}
            ]
        ]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [ 
                {
                    "client_id": 1,
                    "status": "processando",
                    "periodo": "2025-05-26",
                    "items": [
                        {"product_id": 1, "quantity": 1, "price_at_order": 59.99},
                        {"product_id": 3, "quantity": 2, "price_at_order": 25.00}
                    ]
                }
            ]
        }
    )


class OrderItemPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    product_id: int = Field(..., example=1)
    quantity: int = Field(..., example=2)
    price_at_order: float = Field(..., example=59.99)
    product: ProductPublic 


class OrderPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., example=1)
    status: str = Field(..., example="processando")
    periodo: date = Field(..., example=date(2025, 5, 26))
    client_id: int = Field(..., example=1)
    is_active: bool = Field(..., example=True)
    products: List[OrderItemPublic]


class OrderList(BaseModel):
    orders: List[OrderPublic]


class UserSchema(BaseModel):
    username: str = Field(..., example="novo_usuario_exemplo") 
    email: EmailStr = Field(..., example="usuario.novo@dominio.com") 
    password: str = Field(..., example="SenhaSegura123") 


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., example=1)
    username: str = Field(..., example="lucas12345")
    email: EmailStr = Field(..., example="lucas12345@example.com")


class UserList(BaseModel):
    users: List[UserPublic]


class CurrentUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., example=2)
    username: str = Field(..., example="lucas12345")
    email: EmailStr = Field(..., example="lucas12345@example.com")


class Token(BaseModel):
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJsdWNhczEyMzQ1IiwiaWQiOjIsImV4cCI6MTc0ODIyODc2NH0.SiZ4s2xXP5nT_E7KxWeR2Tb3dyeg3vSoKF2s_eBn0XQ")
    token_type: str = Field(..., example="bearer")


class TokenData(BaseModel):
    username: str | None = Field(None, example="lucas12345")


class ClientFilterParams(BaseModel):
    skip: int = Field(0, description="Número de itens a pular (offset).", example=0)
    limit: int = Field(100, description="Número máximo de itens a retornar.", example=10)
    name: Optional[str] = Field(None, description="Filtrar por nome do cliente (parcial, case-insensitive).", example="Maria")
    email: Optional[EmailStr] = Field(None, description="Filtrar por e-mail do cliente (parcial, case-insensitive).", example="example.com")


class ProductFilterParams(BaseModel):
    skip: int = Field(0, description="Número de itens a pular (offset).", example=0)
    limit: int = Field(100, description="Número máximo de itens a retornar.", example=10)
    secao: Optional[str] = Field(None, description="Filtrar por seção do produto (parcial, case-insensitive).", example="Vestuário")
    min_price: Optional[float] = Field(None, description="Filtrar produtos com preço de venda a partir deste valor.", example=20.0)
    max_price: Optional[float] = Field(None, description="Filtrar produtos com preço de venda até este valor.", example=100.0)
    available: Optional[bool] = Field(None, description="Filtrar produtos disponíveis em estoque (True para >0, False para <=0).", example=True)


class OrderFilterParams(BaseModel):
    skip: int = Field(0, description="Número de itens a pular (offset).", example=0)
    limit: int = Field(100, description="Número máximo de itens a retornar.", example=10)
    start_periodo: Optional[date] = Field(None, description="Filtrar pedidos a partir desta data (YYYY-MM-DD).", example=date(2025, 1, 1))
    end_periodo: Optional[date] = Field(None, description="Filtrar pedidos até esta data (YYYY-MM-DD).", example=date(2025, 12, 31))
    product_section: Optional[str] = Field(None, description="Filtrar pedidos que contenham produtos de uma seção específica (parcial, case-insensitive).", example="Eletrônicos")
    status: Optional[str] = Field(None, description="Filtrar por status do pedido (exato, case-insensitive).", example="concluido")
    client_id: Optional[int] = Field(None, description="Filtrar por ID do cliente.", example=1)

class SendMessageToClientBody(BaseModel):
    mensagem: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="O conteúdo da mensagem a ser enviada.",
        example="Olá, seu pedido #123 foi enviado!" 
    )