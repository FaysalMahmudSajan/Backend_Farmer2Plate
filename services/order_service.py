from sqlalchemy.orm import Session
from models.order import Order
from models.order_item import OrderItem
from models.product import Product
from schemas.order_item import OrderItemResponse

# ✅ নতুন অর্ডার তৈরি করার সার্ভিস ফাংশন 
# (এই লজিকটি আমাদের routers/order.py তেও ব্যবহৃত হয়েছে)
def place_order(db: Session, customer_id: int, items: list, delivery_address: str):
    total_price = 0
    order_items_data = []

    # স্টক যাচাই করা এবং মোট দাম হিসেব করা
    for item in items:
        product = db.query(Product).filter(Product.id == item["product_id"]).first()
        if not product:
            return None, f"Product {item['product_id']} not found" # প্রোডাক্ট না পেলে
        if product.stock < item["quantity"]:
            return None, f"Not enough stock for {product.name}" # স্টক কম থাকলে

        total_price += product.price * item["quantity"]
        order_items_data.append((product, item["quantity"]))

    # ডাটাবেসে মূল অর্ডার এন্ট্রি করা
    order = Order(
        customer_id=customer_id,
        total_price=total_price,
        status="pending", # প্রথম অবস্থায় 'pending'
        delivery_address=delivery_address
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    # অর্ডারের ভেতরের আইটেমগুলো ডাটাবেসে সেভ করা এবং প্রোডাক্টের স্টক কমানো
    for product, qty in order_items_data:
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=qty,
            price=product.price
        )
        product.stock -= qty # বিক্রিত পরিমাণ স্টক থেকে বাদ যাবে
        db.add(order_item)

    db.commit()

    # রেসপন্স ডাটা প্রস্তুত করা
    items_response = [
        OrderItemResponse(
            product_id=oi.product_id,
            quantity=oi.quantity,
            price=oi.price
        ) for oi in db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    ]

    return {
        "order_id": order.id,
        "customer_id": order.customer_id,
        "total_price": order.total_price,
        "status": order.status,
        "delivery_address": order.delivery_address,
        "items": items_response
    }, None