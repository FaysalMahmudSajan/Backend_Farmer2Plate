# routers/farmer.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.db import get_db
from models.user import User, UserRole, OTPRecord
from schemas.farmer import FarmerRegister, FarmerLogin, FarmerResponse, FarmerUpdate, RequestOTP
from core.security import hash_password, verify_password, create_access_token, get_current_user
from core.config import settings
from core.email_helper import send_otp_email, generate_otp

# farmer related API
router = APIRouter(prefix="/farmer", tags=["Farmer"])


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
def register_farmer(data: FarmerRegister, db: Session = Depends(get_db)):
    # 1. Verify OTP from OTPRecord table
    otp_record = db.query(OTPRecord).filter(OTPRecord.email == data.email).first()
    if not otp_record or otp_record.otp_code != data.otp:
        raise HTTPException(status_code=400, detail="ভুল ভেরিফিকেশন কোড!")
    
    # Check if phone is already in use
    existing_phone = db.query(User).filter(User.phone == data.phone).first()
    if existing_phone:
        raise HTTPException(status_code=400, detail="ফোন নম্বর ইতিমধ্যে রেজিস্টার করা হয়েছে")

    # Create user only after OTP is verified
    farmer = User(
        name=data.name,
        phone=data.phone,
        email=data.email,
        password=hash_password(data.password),
        role=UserRole.farmer,
        farm_name=data.farm_name,
        farm_address=data.farm_address,
        latitude=data.latitude,
        longitude=data.longitude,
        is_active=True,
        is_verified=True,
        otp_code=None
    )

    db.add(farmer)
    # Remove the OTP record since it's used
    db.delete(otp_record)
    db.commit()
    
    return {"message": "সফলভাবে রেজিস্ট্রেশন সম্পন্ন হয়েছে! এখন লগইন করুন।"}

@router.post("/login")
def login_farmer(data: FarmerLogin, db: Session = Depends(get_db)):
    # if admin login from farmer panel
    if data.email == settings.ADMIN_EMAIL and data.password == settings.ADMIN_PASSWORD:
        token = create_access_token(
            data={"user_id": "admin_id", "role": "admin"}
        )
        return {
            "access_token": token,
            "token_type": "bearer"
        }

    # farmer login
    farmer = db.query(User).filter(
        User.email == data.email,
        User.role == UserRole.farmer
    ).first()

    # if the farmer data not found or password incorrect
    if not farmer or not verify_password(data.password, farmer.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # check if email is verified
    if not farmer.is_verified:
        raise HTTPException(status_code=403, detail="ইমেইল ভেরিফাই করা হয়নি। অনুগ্রহ করে ইমেইলে পাঠানো কোড দিয়ে আগে অ্যাকাউন্ট ভেরিফাই করুন।")

    # if the farmer account is inactive
    if not farmer.is_active:
        raise HTTPException(status_code=403, detail="এই অ্যাকাউন্টটি নিষ্ক্রিয় করা হয়েছে। অনুগ্রহ করে অ্যাডমিনের সাথে যোগাযোগ করুন।")

    # if the farmer login successful then create access token
    token = create_access_token(
        data={"user_id": farmer.id, "role": farmer.role}
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# get farmer profile
@router.get("/profile/{farmer_id}", response_model=FarmerResponse)
def get_farmer(farmer_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.get("user_id") != farmer_id and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    farmer = db.query(User).filter(
        User.id == farmer_id,
        User.role == UserRole.farmer
    ).first()

    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")

    return farmer


# ✅ কৃষকের প্রোফাইল ডাটা আপডেট করা
@router.put("/update/{farmer_id}", response_model=FarmerResponse)
def update_farmer(farmer_id: int, data: FarmerUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.get("user_id") != farmer_id and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    farmer = db.query(User).filter(
        User.id == farmer_id,
        User.role == UserRole.farmer
    ).first()

    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")

    # রিকোয়েস্ট বডিতে শুধু যেসব ভ্যালু দেওয়া হয়েছে সেগুলোই আপডেট করা
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(farmer, key, value)

    db.commit()
    db.refresh(farmer)

    return farmer


# ❌ কৃষকের অ্যাকাউন্ট পারমানেন্টলি ডিলিট করা
@router.delete("/delete/{farmer_id}")
def delete_farmer(farmer_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.get("user_id") != farmer_id and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    farmer = db.query(User).filter(
        User.id == farmer_id,
        User.role == UserRole.farmer
    ).first()

    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")

    db.delete(farmer)
    db.commit()

    return {"message": "Farmer deleted"}