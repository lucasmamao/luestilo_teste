from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from luestilo_api.database import get_session
from luestilo_api.models import Product
from luestilo_api.schemas import ProductList, ProductPublic, ProductSchema, Message
# from luestilo_api.security import get_current_user, CurrentUser # Importe se for proteger rotas

# Define o roteador para recursos de produtos
router = APIRouter(prefix='/products', tags=['products']) # Prefixo e tag no plural

@router.post('/', status_code=HTTPStatus.CREATED, response_model=ProductPublic)
def create_product(product: ProductSchema, session: Session = Depends(get_session)):
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
def read_all_products(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    products = session.scalars(select(Product).offset(skip).limit(limit)).all()
    return {'products': products}


@router.get('/{product_id}', status_code=HTTPStatus.OK, response_model=ProductPublic)
def read_product(product_id: int, session: Session = Depends(get_session)):
    db_product = session.scalar(select(Product).where(Product.id == product_id))
    if not db_product:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Product not found'
        )
    return db_product


@router.put('/{product_id}', status_code=HTTPStatus.OK, response_model=ProductPublic)
def update_product(product_id: int,
    product: ProductSchema,
    session: Session = Depends(get_session)
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
def delete_product(product_id: int, session: Session = Depends(get_session)):
    db_product = session.scalar(select(Product).where(Product.id == product_id))
    if not db_product:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Product not found'
        )
    session.delete(db_product)
    session.commit()
    return {'message': 'Product deleted'}