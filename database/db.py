from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import settings

# ডাটাবেসের টেবিলগুলোর বেইস ক্লাস (Base) তৈরি করা হচ্ছে
Base = declarative_base()

# SQLAlchemy ইঞ্জিন তৈরি করা হচ্ছে যা ডাটাবেসের সাথে কানেকশন স্থাপন করবে
engine = create_engine(settings.DB_CONNECTION)

# ডাটাবেসের সেশন তৈরি করার জন্য LocalSession তৈরি করা হচ্ছে
LocalSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ডাটাবেস সেশন পাওয়ার জন্য ডিপেন্ডেন্সি ফাংশন
# এই ফাংশন প্রতিবার রিকোয়েস্ট আসার পর একটা সেশন দেয় এবং কাজ শেষে তা ক্লোজ করে দেয়
def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()