# routers/customer.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import Response
from sqlalchemy.orm import Session
from io import BytesIO
from PIL import Image

from database.db import get_db
from models.user import User, UserRole, OTPRecord
from models.notification import Notification
from schemas.customer import CustomerRegister, CustomerLogin, CustomerResponse, CustomerUpdate, RequestOTP
from schemas.notification import NotificationResponse
from core.security import hash_password, verify_password, create_access_token, get_current_user
from core.config import settings
from core.email_helper import send_otp_email, generate_otp

MAX_AVATAR_SIZE = 400   
WEBP_QUALITY   = 82     

def compress_avatar(file_bytes: bytes) -> bytes:
    """Avatar image কে WebP এ compress করা"""
    try:
        img = Image.open(BytesIO(file_bytes))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        # Square crop (center)
        w, h = img.size
        min_side = min(w, h)
        left = (w - min_side) // 2
        top  = (h - min_side) // 2
        img = img.crop((left, top, left + min_side, top + min_side))
        # Resize
        img = img.resize((MAX_AVATAR_SIZE, MAX_AVATAR_SIZE), Image.Resampling.LANCZOS)
        output = BytesIO()
        img.save(output, format="WEBP", quality=WEBP_QUALITY, optimize=True)
        return output.getvalue()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"ছবি প্রসেস করতে সমস্যা: {str(e)}")

router = APIRouter(prefix="/customer", tags=["Customer"])

@router.post("/request-otp")
def request_otp(data: RequestOTP, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="ইমেইল ইতিমধ্যে রেজিস্টার করা হয়েছে!")
    
    otp = generate_otp()
    
    otp_record = db.query(OTPRecord).filter(OTPRecord.email == data.email).first()
    if otp_record:
        otp_record.otp_code = otp
    else:
        otp_record = OTPRecord(email=data.email, otp_code=otp)
        db.add(otp_record)
    
    db.commit()
    
    try:
        send_otp_email(data.email, otp)
    except Exception as e:
        print(f"Email error: {e}")
        raise HTTPException(status_code=500, detail="ইমেইল পাঠাতে সমস্যা হয়েছে!")
        
    return {"message": "আপনার ইমেইলে ৫-ডিজিটের ভেরিফিকেশন কোড পাঠানো হয়েছে।"}

# Final register after OTP verification
@router.post("/register")
def register_customer(data: CustomerRegister, db: Session = Depends(get_db)):
    # 1. Verify OTP from OTPRecord table
    otp_record = db.query(OTPRecord).filter(OTPRecord.email == data.email).first()
    if not otp_record or otp_record.otp_code != data.otp:
        raise HTTPException(status_code=400, detail="ভুল ভেরিফিকেশন কোড!")
    
    # Check if phone is already in use
    existing_phone = db.query(User).filter(User.phone == data.phone).first()
    if existing_phone:
        raise HTTPException(status_code=400, detail="ফোন নম্বর ইতিমধ্যে রেজিস্টার করা হয়েছে")

    # Create user only after OTP is verified
    customer = User(
        name=data.name,
        phone=data.phone,
        email=data.email,
        password=hash_password(data.password),
        role=UserRole.customer,
        address=data.address,
        latitude=data.latitude,
        longitude=data.longitude,
        is_active=True,
        is_verified=True,
        otp_code=None
    )

    db.add(customer)
    # Remove the OTP record since it's used
    db.delete(otp_record)
    db.commit()
    
    return {"message": "সফলভাবে রেজিস্ট্রেশন সম্পন্ন হয়েছে! এখন লগইন করুন।"}


@router.post("/login")
def login_customer(data: CustomerLogin, db: Session = Depends(get_db)):
    customer = db.query(User).filter(
        User.email == data.email,
        User.role == UserRole.customer
    ).first()

    if not customer or not verify_password(data.password, customer.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    if not customer.is_verified:
        raise HTTPException(status_code=403, detail="ইমেইল ভেরিফাই করা হয়নি। অনুগ্রহ করে ইমেইলে পাঠানো কোড দিয়ে আগে অ্যাকাউন্ট ভেরিফাই করুন।")

    if not customer.is_active:
        raise HTTPException(status_code=403, detail="এই অ্যাকাউন্টটি নিষ্ক্রিয় করা হয়েছে। অনুগ্রহ করে অ্যাডমিনের সাথে যোগাযোগ করুন।")

    token = create_access_token(
        data={"user_id": customer.id, "role": customer.role}
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.get("/profile/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.get("user_id") != customer_id and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    customer = db.query(User).filter(
        User.id == customer_id,
        User.role == UserRole.customer
    ).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    resp = CustomerResponse.model_validate(customer)
    resp.has_profile_picture = bool(customer.profile_picture_data)
    return resp

@router.put("/update/{customer_id}", response_model=CustomerResponse)
def update_customer(customer_id: int, data: CustomerUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.get("user_id") != customer_id and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    customer = db.query(User).filter(
        User.id == customer_id,
        User.role == UserRole.customer
    ).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(customer, key, value)

    db.commit()
    db.refresh(customer)

    resp = CustomerResponse.model_validate(customer)
    resp.has_profile_picture = bool(customer.profile_picture_data)
    return resp

@router.delete("/delete/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.get("user_id") != customer_id and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    customer = db.query(User).filter(
        User.id == customer_id,
        User.role == UserRole.customer
    ).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    db.delete(customer)
    db.commit()

    return {"message": "Customer deleted"}

@router.post("/profile-picture/{customer_id}")
async def upload_customer_profile_picture(
    customer_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("user_id") != customer_id and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    customer = db.query(User).filter(
        User.id == customer_id,
        User.role == UserRole.customer
    ).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    allowed_types = {"image/jpeg", "image/png", "image/webp", "image/gif", "image/bmp"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="শুধু JPEG, PNG, WebP, GIF অথবা BMP ফাইল আপলোড করতে পারবেন!")

    file_bytes = await file.read()

    if len(file_bytes) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="ছবি সর্বোচ্চ ৫MB হতে পারবে!")

    compressed = compress_avatar(file_bytes)

    customer.profile_picture_data = compressed
    customer.profile_picture_type = "image/webp"
    db.commit()

    return {"message": "প্রোফাইল পিকচার আপলোড হয়েছে!", "has_profile_picture": True}

@router.get("/profile-picture/{customer_id}")
def serve_customer_profile_picture(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(User).filter(
        User.id == customer_id,
        User.role == UserRole.customer
    ).first()

    if not customer or not customer.profile_picture_data:
        raise HTTPException(status_code=404, detail="Profile picture not found")

    return Response(
        content=customer.profile_picture_data,
        media_type=customer.profile_picture_type or "image/webp",
        headers={
            "Cache-Control": "public, max-age=3600",
            "Content-Disposition": f'inline; filename="avatar_{customer_id}.webp"'
        }
    )

@router.get("/notifications", response_model=list[NotificationResponse])
def get_customer_notifications(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authorized")
    
    notifications = db.query(Notification).filter(
        Notification.user_id == user_id
    ).order_by(Notification.created_at.desc()).all()
    
    return notifications

@router.put("/notifications/{notification_id}/read")
def mark_notification_read(notification_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("user_id")
    notif = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == user_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notif.is_read = True
    db.commit()
    return {"message": "Notification marked as read"}

@router.delete("/notifications/{notification_id}")
def delete_customer_notification(notification_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("user_id")
    notif = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == user_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    db.delete(notif)
    db.commit()
    return {"message": "Notification deleted"}