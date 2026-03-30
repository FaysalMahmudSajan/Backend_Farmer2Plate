from sqlalchemy.orm import Session
from models.user import User, UserRole
from core.security import hash_password, verify_password

# ✅ নতুন ইউজার (কৃষক/ক্রেতা) রেজিস্টার করার সার্ভিস ফাংশন 
def register_user(db: Session, name: str, phone: str, password: str, role: UserRole, **kwargs):
    # প্রথমে চেক করা হচ্ছে এই নাম্বারে আগে থেকে একাউন্ট আছে কিনা
    existing = db.query(User).filter(User.phone == phone).first()
    if existing:
        return None, "Phone already registered" # থাকলে এরর দেবে

    # নতুন ইউজারের ডাটাবেস এন্ট্রি তৈরি করা
    user = User(
        name=name,
        phone=phone,
        password=hash_password(password), # পাসওয়ার্ড হ্যাশ করে নিরাপদ রাখা
        role=role,
        **kwargs
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user, None


# ✅ ইউজার লগইন ভেরিফিকেশন (অথেনটিকেশন)
def authenticate_user(db: Session, phone: str, password: str, role: UserRole):
    # নাম্বার এবং রোল দিয়ে ইউজারকে খোঁজা
    user = db.query(User).filter(User.phone == phone, User.role == role).first()
    
    # ইউজার না পেলে অথবা পাসওয়ার্ড ভুল হলে None রিটার্ন করবে
    if not user or not verify_password(password, user.password):
        return None
        
    return user


# ✅ ইউজারের প্রোফাইল আপডেট করা
def update_user(db: Session, user: User, updates: dict):
    # যে যে ডাটা আপডেট করতে দেওয়া হয়েছে সেগুলো ডাটাবেসে সেভ করা
    for key, value in updates.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user