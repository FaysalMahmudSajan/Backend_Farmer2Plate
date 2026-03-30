# routers/admin.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from database.db import get_db
from models.user import User, UserRole
from models.product import Product
from models.order import Order
from models.order_item import OrderItem
from schemas.admin import AdminLogin, AdminLoginResponse
from schemas.product import ProductResponse
from schemas.order import OrderResponse
from schemas.order_item import OrderItemResponse
from core.security import verify_password, create_access_token, get_current_admin
from core.config import settings

# অ্যাডমিন প্যানেলের জন্য API রাউটার
router = APIRouter(prefix="/admin", tags=["Admin"])


# ✅ অ্যাডমিন লগইন (Admin Login)
@router.post("/login", response_model=AdminLoginResponse)
def login_admin(data: AdminLogin, db: Session = Depends(get_db)):
    # .env ফাইলে থাকা অ্যাডমিনের নাম্বারের সাথে মিলিয়ে চেক করা
    admin = db.query(User).filter(
        User.email == settings.ADMIN_EMAIL,
        User.role == "admin"
    ).first()

    # অ্যাডমিন ডাটাবেসে না থাকলে বা পাসওয়ার্ড না মিললে
    if not admin or not (data.password == settings.ADMIN_PASSWORD):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # সফল লগইনে টোকেন তৈরি করা
    token = create_access_token(data={"user_id": admin.id, "role": admin.role})

    return {"access_token": token, "token_type": "bearer"}


# ✅ সমস্ত ইউজার ম্যানেজ করা (শুধুমাত্র অ্যাডমিনের জন্য)
@router.get("/users")
def get_all_users(current_admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    return db.query(User).all()


# ❌ যেকোনো ইউজারকে ডিলিট করা
@router.delete("/user/{user_id}")
def delete_user(user_id: int, current_admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # অ্যাডমিন নিজেকে ডিলিট করতে পারবে না
    if user.id == current_admin["user_id"]:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}


# 🛑 ইউজারের স্ট্যাটাস অন/অফ করা (ফ্রিজ/অ্যাক্টিভ করা)
@router.put("/user/{user_id}/toggle-status")
def toggle_user_status(user_id: int, current_admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # অ্যাডমিন নিজেকে ফ্রিজ করতে পারবে না
    if user.id == current_admin["user_id"]:
        raise HTTPException(status_code=400, detail="Cannot freeze yourself")
    
    # স্ট্যাটাস পরিবর্তন করা হচ্ছে (ট্রু থাকলে ফলস, ফলস থাকলে ট্রু)
    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    return {"message": "User status updated", "is_active": user.is_active}


# ✅ সমস্ত প্রোডাক্ট ম্যানেজ করা (শুধুমাত্র অ্যাডমিনের জন্য)
@router.get("/products", response_model=list[ProductResponse])
def get_all_products(current_admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    return db.query(Product).options(joinedload(Product.images)).all()


# ❌ যেকোনো প্রোডাক্ট মুছে ফেলা
@router.delete("/product/{product_id}")
def delete_product(product_id: int, current_admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(product)
    db.commit()
    return {"message": "Product deleted"}


# ✅ সিস্টেমের সমস্ত অর্ডার এক সাথে দেখা (শুধুমাত্র অ্যাডমিনের জন্য)
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


# ✏️ অর্ডারের স্ট্যাটাস পরিবর্তন করা (শুধুমাত্র অ্যাডমিনের জন্য)
@router.put("/order/{order_id}/status")
def update_order_status(order_id: int, body: dict, current_admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    allowed = {"pending", "accepted", "shipped", "delivered"}
    status = body.get("status", "")
    if status not in allowed:
        raise HTTPException(status_code=400, detail=f"Invalid status. Allowed: {allowed}")
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = status
    db.commit()
    db.refresh(order)
    return {"message": "Status updated", "status": order.status}