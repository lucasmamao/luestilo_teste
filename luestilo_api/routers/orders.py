from http import HTTPStatus
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from luestilo_api.database import get_session
from luestilo_api.models import Client, Order, OrderProduct, Product
from luestilo_api.schemas import OrderCreateSchema, OrderList, OrderPublic, Message
# from luestilo_api.security import get_current_user, CurrentUser # Importe se for proteger rotas

# Define o roteador para recursos de pedidos
router = APIRouter(prefix='/orders', tags=['orders']) # Prefixo e tag no plural

@router.post('/', status_code=HTTPStatus.CREATED, response_model=OrderPublic)
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


@router.get('/', status_code=HTTPStatus.OK, response_model=OrderList)
def read_all_orders(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    orders = session.scalars(
        select(Order)
        .options(joinedload(Order.products).joinedload(OrderProduct.product))
        .offset(skip).limit(limit)
    ).unique().all()
    return {'orders': orders}


@router.get('/{order_id}', status_code=HTTPStatus.OK, response_model=OrderPublic)
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


@router.put('/{order_id}', status_code=HTTPStatus.OK, response_model=OrderPublic)
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


@router.delete('/{order_id}', status_code=HTTPStatus.OK, response_model=Message)
def delete_order(order_id: int, session: Session = Depends(get_session)):
    db_order = session.scalar(select(Order).where(Order.id == order_id))
    if not db_order:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Order not found'
        )
    session.delete(db_order)
    session.commit()
    return {'message': 'Order deleted'}