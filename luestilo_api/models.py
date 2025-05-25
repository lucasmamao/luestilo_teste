import json
from datetime import date
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    String,
    Float,
    Text
)
from sqlalchemy.orm import (
    Mapped, mapped_column, registry, relationship
)
from sqlalchemy.types import TypeDecorator



table_registry = registry()
Base = table_registry.generate_base()



class JSONList(TypeDecorator):
    impl = Text
    cache_ok = True
    def process_bind_param(self, value, dialect):
        if value is not None: return json.dumps(value)
        return value
    def process_result_value(self, value, dialect):
        if value is not None: return json.loads(value)
        return value


# --- MODELOS ---

@table_registry.mapped_as_dataclass
class Client(Base):
    __tablename__ = 'clients'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(100))
    cpf: Mapped[str] = mapped_column(String(14), unique=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    orders: Mapped[List['Order']] = relationship(
        back_populates='client',
        default_factory=list,
        init=False
    )


@table_registry.mapped_as_dataclass
class Product(Base):
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    descricao: Mapped[str] = mapped_column(String(255))
    valor_de_venda: Mapped[float] = mapped_column(Float)
    codigo_de_barras: Mapped[str] = mapped_column(String(50), unique=True)
    secao: Mapped[str] = mapped_column(String(100))
    estoque_inicial: Mapped[int] = mapped_column(Integer)
    data_validade: Mapped[Optional[date]] = mapped_column(nullable=True)
    imagens: Mapped[List[str]] = mapped_column(JSONList, default_factory=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    order_items: Mapped[List['OrderProduct']] = relationship(
        back_populates='product',
        default_factory=list,
        init=False
    )


@table_registry.mapped_as_dataclass
class Order(Base):
    __tablename__ = 'orders'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status: Mapped[str] = mapped_column(String(50))
    periodo: Mapped[date] 

    client_id: Mapped[int] = mapped_column(Integer, ForeignKey('clients.id'))
    client: Mapped['Client'] = relationship(
        back_populates='orders',
        init=False
    )

    products: Mapped[List['OrderProduct']] = relationship(
        back_populates='order',
        default_factory=list,
        init=False
    )


@table_registry.mapped_as_dataclass
class OrderProduct(Base):
    __tablename__ = 'order_products'
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey('orders.id'), primary_key=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey('products.id'), primary_key=True)
    quantity: Mapped[int] = mapped_column(Integer)
    price_at_order: Mapped[float] = mapped_column(Float)

    order: Mapped['Order'] = relationship(back_populates='products', init=False)
    product: Mapped['Product'] = relationship(back_populates='order_items', init=False)


@table_registry.mapped_as_dataclass
class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(100), unique=True)