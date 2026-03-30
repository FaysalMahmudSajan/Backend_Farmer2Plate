# routers/order.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import get_db
from models.order import Order
from models.order_item import OrderItem
from models.product import Product
from schemas.order import OrderCreate, OrderResponse
from schemas.order_item import OrderItemResponse
from core.security import get_current_user

# অর্ডার সংক্রান্ত API গুচ্ছের রাউটার
router = APIRouter(prefix="/order", tags=["Order"])


# ✅ অর্ডার প্লেস করার API (শুধুমাত্র কাস্টমারদের জন্য)
@router.post("/place", response_model=OrderResponse)
def place_order(data: OrderCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] != "customer":
        raise HTTPException(status_code=403, detail="Only customers can place orders") # শুধুমাত্র কাস্টমাররাই অর্ডার করতে পারবেন

    total_price = 0
    order_items = []

    # স্টক যাচাই করা এবং মোট দাম হিসেব করা
    for item in data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found") # প্রোডাক্ট না পাওয়া গেলে
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough stock for {product.name}") # স্টক কম থাকলে

        total_price += product.price * item.quantity # মোট দাম যোগ করা হচ্ছে
        order_items.append((product, item.quantity))

    # মূল অর্ডার তৈরি করা
    order = Order(
        customer_id=current_user["user_id"],
        total_price=total_price,
        status="pending", # প্রথম অবস্থায় পেন্ডিং
        delivery_address=data.delivery_address,
        payment_method=data.payment_method or "cod"  # পেমেন্ট পদ্ধতি সেভ করা
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    # অর্ডারের আইটেমগুলো ডাটাবেসে তৈরি করা এবং স্টক কমানো
    for product, qty in order_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=qty,
            price=product.price
        )
        product.stock -= qty # প্রোডাক্টের মূল স্টক থেকে বিক্রি হওয়া পরিমাণ বিয়োগ করা
        db.add(order_item)

    db.commit()

    # ফ্রন্টএন্ডে পাঠানোর জন্য রেসপন্স তৈরি করা
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


# ✅ নিজের করা অর্ডারগুলোর লিস্ট দেখার API (কাস্টমারদের জন্য)
@router.get("/my-orders", response_model=list[OrderResponse])
def my_orders(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] != "customer":
        raise HTTPException(status_code=403, detail="Only customers can view orders")

    # কাস্টমারের নিজের করা সব অর্ডার ডাটাবেস থেকে তুলে আনা
    orders = db.query(Order).filter(Order.customer_id == current_user["user_id"]).all()
    response = []
    
    # প্রতিটি অর্ডারের আইটেমগুলো যোগ করে রেসপন্স তৈরি করা
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