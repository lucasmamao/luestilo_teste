import json
from datetime import date
from typing import List, Optional

from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship
from sqlalchemy.types import Text, TypeDecorator

table_registry = registry()


class JSONList(TypeDecorator):
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return value


@table_registry.mapped_as_dataclass
class Client:
    __tablename__ = 'clients'
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    cpf: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    orders: Mapped[List['Order']] = relationship(
        back_populates='client',
        default_factory=list,
        init=False
    )


@table_registry.mapped_as_dataclass
class Product:
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    descricao: Mapped[str]
    valor_de_venda: Mapped[float]
    codigo_de_barras: Mapped[str] = mapped_column(unique=True)
    secao: Mapped[str]
    estoque_inicial: Mapped[int]
    data_validade: Mapped[Optional[date]]
    imagens: Mapped[List[str]] = mapped_column(JSONList, default_factory=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    order_items: Mapped[List['OrderProduct']] = relationship(
        back_populates='product',
        default_factory=list,
        init=False
    )


@table_registry.mapped_as_dataclass
class Order:
    __tablename__ = 'orders'
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    status: Mapped[str]
    periodo: Mapped[date]
    client_id: Mapped[int] = mapped_column(ForeignKey('clients.id'))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

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
class OrderProduct:
    __tablename__ = 'order_products'
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), primary_key=True)
    quantity: Mapped[int]
    price_at_order: Mapped[float]

    order: Mapped['Order'] = relationship(back_populates='products', init=False)
    product: Mapped['Product'] = relationship(back_populates='order_items', init=False)


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
