from sqlalchemy.orm import Session
from models.order import Order
from models.order_item import OrderItem
from models.product import Product
from schemas.order_item import OrderItemResponse


def place_order(db: Session, customer_id: int, items: list, delivery_address: str):
    total_price = 0
    order_items_data = []

    for item in items:
        product = db.query(Product).filter(Product.id == item["product_id"]).first()
        if not product:
            return None, f"Product {item['product_id']} not found" 
        if product.stock < item["quantity"]:
            return None, f"Not enough stock for {product.name}" 

        total_price += product.price * item["quantity"]
        order_items_data.append((product, item["quantity"]))

    order = Order(
        customer_id=customer_id,
        total_price=total_price,
        status="pending",
        delivery_address=delivery_address
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    for product, qty in order_items_data:
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