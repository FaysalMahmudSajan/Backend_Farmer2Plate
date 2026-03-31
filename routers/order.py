

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import get_db
from models.order import Order
from models.order_item import OrderItem
from models.product import Product
from schemas.order import OrderCreate, OrderResponse
from schemas.order_item import OrderItemResponse
from core.security import get_current_user


router = APIRouter(prefix="/order", tags=["Order"])



@router.post("/place", response_model=OrderResponse)
def place_order(data: OrderCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] != "customer":
        raise HTTPException(status_code=403, detail="Only customers can place orders")

    total_price = 0
    order_items = []

    for item in data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found") 
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough stock for {product.name}") 

        total_price += product.price * item.quantity 
        order_items.append((product, item.quantity))

    order = Order(
        customer_id=current_user["user_id"],
        total_price=total_price,
        status="pending", 
        delivery_address=data.delivery_address,
        payment_method=data.payment_method or "cod"  
    )

    db.add(order)
    db.commit()
    db.refresh(order)


    for product, qty in order_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=qty,
            price=product.price
        )
        product.stock -= qty
        db.add(order_item)

    db.commit()

    items_response = [
        OrderItemResponse(product_id=oi.product_id, quantity=oi.quantity, price=oi.price)
        for oi in db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    ]

    return OrderResponse(
        id=order.id,
        customer_id=order.customer_id,
        total_price=order.total_price,
        status=order.status,
        delivery_address=order.delivery_address,
        payment_method=order.payment_method,
        created_at=str(order.created_at) if order.created_at else None,
        items=items_response
    )



@router.get("/my-orders", response_model=list[OrderResponse])
def my_orders(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] != "customer":
        raise HTTPException(status_code=403, detail="Only customers can view orders")


    orders = db.query(Order).filter(Order.customer_id == current_user["user_id"]).all()
    response = []
    

    for order in orders:
        items = [
            OrderItemResponse(
                product_id=oi.product_id,
                quantity=oi.quantity,
                price=oi.price
            )
            for oi in db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        ]
        response.append(OrderResponse(
            id=order.id,
            customer_id=order.customer_id,
            total_price=order.total_price,
            status=order.status,
            delivery_address=order.delivery_address,
            payment_method=order.payment_method,
            created_at=str(order.created_at) if order.created_at else None,
            items=items
        ))
    return response