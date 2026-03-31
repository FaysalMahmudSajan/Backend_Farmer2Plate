from sqlalchemy.orm import Session
from models.user import User, UserRole
from core.security import hash_password, verify_password

def register_user(db: Session, name: str, phone: str, password: str, role: UserRole, **kwargs):

    existing = db.query(User).filter(User.phone == phone).first()
    if existing:
        return None, "Phone already registered" 

    user = User(
        name=name,
        phone=phone,
        password=hash_password(password), 
        role=role,
        **kwargs
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user, None


def authenticate_user(db: Session, phone: str, password: str, role: UserRole):

    user = db.query(User).filter(User.phone == phone, User.role == role).first()

    if not user or not verify_password(password, user.password):
        return None
        
    return user


def update_user(db: Session, user: User, updates: dict):

    for key, value in updates.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user