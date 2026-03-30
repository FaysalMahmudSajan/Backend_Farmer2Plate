# routers/customer.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.db import get_db
from models.user import User, UserRole, OTPRecord
from schemas.customer import CustomerRegister, CustomerLogin, CustomerResponse, CustomerUpdate, RequestOTP
from core.security import hash_password, verify_password, create_access_token, get_current_user
from core.config import settings
from core.email_helper import send_otp_email, generate_otp


# কাস্টমারের জন্য API গুচ্ছের রাউটার
router = APIRouter(prefix="/customer", tags=["Customer"])


# Send OTP to email before register
@router.post("/request-otp")
def request_otp(data: RequestOTP, db: Session = Depends(get_db)):
    # Check if email is already in use
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="ইমেইল ইতিমধ্যে রেজিস্টার করা হয়েছে!")
    
    otp = generate_otp()
    
    # Store OTP temporarily in OTPRecord table
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
        raise HTTPException(status_code=500, detail="ইমেইল পাঠাতে সমস্যা হয়েছে!")
        
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
    
    return {"message": "সফলভাবে রেজিস্ট্রেশন সম্পন্ন হয়েছে! এখন লগইন করুন।"}


# ✅ কাস্টমার লগইন (JWT)
@router.post("/login")
def login_customer(data: CustomerLogin, db: Session = Depends(get_db)):
    customer = db.query(User).filter(
        User.email == data.email,
        User.role == UserRole.customer
    ).first()

    if not customer or not verify_password(data.password, customer.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    if not customer.is_verified:
        raise HTTPException(status_code=403, detail="ইমেইল ভেরিফাই করা হয়নি। অনুগ্রহ করে ইমেইলে পাঠানো কোড দিয়ে আগে অ্যাকাউন্ট ভেরিফাই করুন।")

    if not customer.is_active:
        raise HTTPException(status_code=403, detail="এই অ্যাকাউন্টটি নিষ্ক্রিয় করা হয়েছে। অনুগ্রহ করে অ্যাডমিনের সাথে যোগাযোগ করুন।")

    # সফল হলে টোকেন তৈরি করা
    token = create_access_token(
        data={"user_id": customer.id, "role": customer.role}
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# ✅ কাস্টমারের প্রোফাইল ডাটা রিড করা
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

    return customer


# ✅ কাস্টমারের প্রোফাইল আপডেট করা
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

    # রিকোয়েস্টে যে ভ্যালুগুলো দেওয়া হয়েছে শুধুমাত্র সেগুলোই আপডেট করা
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(customer, key, value)

    db.commit()
    db.refresh(customer)

    return customer


# ❌ কাস্টমারের অ্যাকাউন্ট ডিলিট করা
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