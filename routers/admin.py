# routers/admin.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from database.db import get_db
from models.user import User, UserRole
from models.product import Product
from models.order import Order
from models.order_item import OrderItem
from models.notification import Notification
from schemas.admin import AdminLogin, AdminLoginResponse
from schemas.product import ProductResponse
from schemas.order import OrderResponse
from schemas.order_item import OrderItemResponse
from core.security import verify_password, create_access_token, get_current_admin
from core.config import settings

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/login", response_model=AdminLoginResponse)
def login_admin(data: AdminLogin, db: Session = Depends(get_db)):

    admin = db.query(User).filter(
        User.email == settings.ADMIN_EMAIL,
        User.role == "admin"
    ).first()

    if not admin or not (data.password == settings.ADMIN_PASSWORD):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data={"user_id": admin.id, "role": admin.role})

    return {"access_token": token, "token_type": "bearer"}

@router.get("/users")
def get_all_users(current_admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    users = db.query(User).all()
    result = []
    for u in users:
        result.append({
            "id": u.id,
            "name": u.name,
            "phone": u.phone,
            "email": u.email,
            "role": u.role.value if hasattr(u.role, 'value') else str(u.role),
            "is_active": u.is_active,
            "is_verified": u.is_verified,
            "address": u.address,
            "latitude": u.latitude,
            "longitude": u.longitude,
            "farm_name": getattr(u, 'farm_name', None),
            "farm_address": getattr(u, 'farm_address', None),
            "has_profile_picture": bool(u.profile_picture_data),
            "created_at": str(u.created_at) if u.created_at else None,
        })
    return result

@router.delete("/user/{user_id}")
def delete_user(user_id: int, current_admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.id == current_admin["user_id"]:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}

@router.put("/user/{user_id}/toggle-status")
def toggle_user_status(user_id: int, current_admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.id == current_admin["user_id"]:
        raise HTTPException(status_code=400, detail="Cannot freeze yourself")

    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    return {"message": "User status updated", "is_active": user.is_active}

@router.get("/products", response_model=list[ProductResponse])
def get_all_products(current_admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    return db.query(Product).options(joinedload(Product.images)).all()

@router.delete("/product/{product_id}")
def delete_product(product_id: int, current_admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(product)
    db.commit()
    return {"message": "Product deleted"}

@router.get("/orders")
def get_all_orders(current_admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    orders = db.query(Order).options(joinedload(Order.items)).all()
    response = []
    for order in orders:
        items = [
            OrderItemResponse(product_id=oi.product_id, quantity=oi.quantity, price=oi.price)
            for oi in order.items
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

@router.put("/order/{order_id}/status")
def update_order_status(order_id: int, body: dict, current_admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    allowed = {"pending", "accepted", "shipped", "delivered", "cancelled"}
    status = body.get("status", "")
    if status not in allowed:
        raise HTTPException(status_code=400, detail=f"Invalid status. Allowed: {allowed}")
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if status == "accepted" and order.status != "accepted":
        farmer_ids = set()
        for item in order.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product and product.farmer_id:
                farmer_ids.add(product.farmer_id)
        
        for fid in farmer_ids:
            notification = Notification(
                user_id=fid,
                message=f"🎉 আপনার একটি পণ্য অর্ডার #{order.id}-এ নেওয়া হয়েছে!"
            )
            db.add(notification)
            
    if status == "cancelled" and order.status != "cancelled":
        if order.customer_id:
            notification = Notification(
                user_id=order.customer_id,
                message=f"❌ দুঃখিত, আপনার অর্ডার #{order.id} প্রস্তুতকারকের সমস্যার কারণে বাতিল করা হয়েছে!"
            )
            db.add(notification)

    order.status = status
    db.commit()
    db.refresh(order)
    return {"message": "Status updated", "status": order.status}