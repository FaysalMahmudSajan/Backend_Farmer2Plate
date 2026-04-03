# models/product_image.py

from sqlalchemy import Column, Integer, ForeignKey, LargeBinary, String
from sqlalchemy.orm import relationship
from database.db import Base

# প্রোডাক্টের ছবির জন্য ডাটাবেস মডেল (product_images টেবিল তৈরি করবে)
class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, index=True) # ছবির ইউনিক আইডি

    # কোন প্রোডাক্টের ছবি সেটি বোঝাতে Foreign Key
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))

    image_data = Column(LargeBinary, nullable=False)      # বাইনারী ডাটা হিসেবে ছবি সংরক্ষণ করা হবে (WebP/JPEG ফরমেটে)
    content_type = Column(String, default="image/webp")   # ছবির ধরন বা MIME টাইপ
    filename = Column(String, nullable=True)              # ছবির আসল নাম
    position = Column(Integer, default=0)                 # ছবির সিরিয়াল বা পজিশন (যেমন ০-৪)

    # রিলেশনশিপ
    product = relationship("Product", back_populates="images") # প্রোডাক্টের সাথে ছবির সম্পর্ক
