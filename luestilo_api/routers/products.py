from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Optional

from luestilo_api.security import get_current_user
from luestilo_api.database import get_session
from luestilo_api.models import Product
from luestilo_api.schemas import ProductList, ProductPublic, ProductSchema, Message, CurrentUser

router = APIRouter(prefix='/products', tags=['products']) 

@router.post('/', status_code=HTTPStatus.CREATED, response_model=ProductPublic)
def create_product(
    product: ProductSchema, 
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user)
):
    db_product = session.scalar(
        select(Product).where(Product.codigo_de_barras == product.codigo_de_barras)
    )
    if db_product:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Product with this barcode already exists',
        )

    db_product = Product(**product.model_dump())
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product


@router.get('/', status_code=HTTPStatus.OK, response_model=ProductList)
def read_all_products(
    skip: int = 0,
    limit: int = 100,
    secao: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    available: Optional[bool] = Query(None),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user)
):
    query = select(Product).where(Product.is_active == True)

    if secao:
        query = query.where(Product.secao.ilike(f'%{secao}%'))

    if min_price is not None:
        query = query.where(Product.valor_de_venda >= min_price)

    if max_price is not None:
        query = query.where(Product.valor_de_venda <= max_price)

    if available is True:
        query = query.where(Product.estoque_inicial > 0)
    elif available is False:
        query = query.where(Product.estoque_inicial <= 0)

    query = query.offset(skip).limit(limit)

    products = session.scalars(query).all()

    return {'products': products}


@router.get('/{product_id}', status_code=HTTPStatus.OK, response_model=ProductPublic)
def read_product(
    product_id: int, 
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user)
):
    db_product = session.scalar(select(Product).where(Product.id == product_id))
    if not db_product:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Product not found'
        )
    return db_product


@router.put('/{product_id}', status_code=HTTPStatus.OK, response_model=ProductPublic)
def update_product(product_id: int,
    product: ProductSchema,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user)
):
    db_product = session.scalar(select(Product).where(Product.id == product_id))
    if not db_product:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Product not found'
        )

    if db_product.codigo_de_barras != product.codigo_de_barras:
        existing_product = session.scalar(
            select(Product).where(
                (Product.id != product_id) &
                (Product.codigo_de_barras == product.codigo_de_barras)
            )
        )
        if existing_product:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Product with this barcode already exists for another product',
            )

    for key, value in product.model_dump(exclude_unset=True).items():
        setattr(db_product, key, value)

    session.commit()
    session.refresh(db_product)
    return db_product


@router.delete('/{product_id}', status_code=HTTPStatus.OK, response_model=Message)
def delete_product(
    product_id: int,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user)):
    db_product = session.scalar(select(Product).where(Product.id == product_id))
    if not db_product:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Product not found'
        )
    db_product.is_active = False
    session.add(db_product)
    session.commit()
    return {'message': 'Product deleted'}

@router.patch('/products/{product_id}/reactivate', status_code=HTTPStatus.OK, response_model=ProductPublic)
def reactivate_product(
    product_id: int,
    quantity_to_add: int = Query(..., ge=1, description="Quantidade a ser adicionada ao estoque do produto (deve ser maior ou igual a 1)"), 
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user)
):
    db_product = session.scalar(select(Product).where(Product.id == product_id))

    if not db_product:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Product not found'
        )
    db_product.is_active = True
    
   
    db_product.estoque_inicial += quantity_to_add

    session.add(db_product)
    session.commit()
    session.refresh(db_product)

    return db_product