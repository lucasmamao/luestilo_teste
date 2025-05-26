from datetime import date
from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from luestilo_api.database import get_session
from luestilo_api.models import Client, Order, OrderProduct, Product
from luestilo_api.schemas import Message, OrderCreateSchema, OrderList, OrderPublic

router = APIRouter(prefix='/orders', tags=['orders'])


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

        requested_quantity = item_data.quantity
        if db_product.estoque_inicial < requested_quantity:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=f'Insufficient stock for product {db_product.descricao}. Available: {db_product.estoque_inicial}, Requested: {requested_quantity}',
            )

        db_product.estoque_inicial -= requested_quantity
        session.add(db_product)

        price_to_use = item_data.price_at_order if item_data.price_at_order is not None else db_product.valor_de_venda

        db_order_product = OrderProduct(
            order_id=db_order.id,
            product_id=db_product.id,
            quantity=requested_quantity,
            price_at_order=price_to_use
        )
        session.add(db_order_product)

    session.commit()
    session.refresh(db_order)
    return db_order


@router.get('/', status_code=HTTPStatus.OK, response_model=OrderList)
def read_all_orders(
    skip: int = 0,
    limit: int = 100,
    start_periodo: Optional[date] = Query(None),
    end_periodo: Optional[date] = Query(None),
    product_section: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    client_id: Optional[int] = Query(None),
    session: Session = Depends(get_session)
):
    query = select(Order).where(Order.is_active == True)

    if status:
        query = query.where(Order.status.ilike(status))

    if client_id is not None:
        query = query.where(Order.client_id == client_id)

    if start_periodo:
        query = query.where(Order.periodo >= start_periodo)
    if end_periodo:
        query = query.where(Order.periodo <= end_periodo)

    if product_section:
        query = query.join(Order.products).join(OrderProduct.product).where(Product.secao.ilike(f'%{product_section}%'))

    query = query.options(joinedload(Order.products).joinedload(OrderProduct.product))

    query = query.offset(skip).limit(limit)

    orders = session.scalars(query).unique().all()

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

    db_order.is_active = False
    session.add(db_order)
    session.commit()
    session.refresh(db_order)
    return {'message': 'Order deleted'}
