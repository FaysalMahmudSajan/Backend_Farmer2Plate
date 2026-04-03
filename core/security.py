# core/security.py

from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from core.config import settings

# 🔑 make password hash (encrypt)
def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt() # salt created for database security
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

# compare password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False

# create access token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()

    # set expire time
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode.update({"exp": expire})
    # create token using algorithm
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt

# decode token
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

# 🛡️ API রিকোয়েস্টে পাঠানো বেয়ারার টোকেন যাচাই করে বর্তমান ইউজারকে বের করা
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_access_token(token)

    # যদি টোকেন ভুল হয় বা মেয়াদ শেষ হয়ে যায়
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return payload

# 🔑 কোনো API-তে শুধুমাত্র অ্যাডমিন যেন ঢুকতে পারে সেটি ভেরিফাই করার ডিপেন্ডেন্সি
def get_current_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user