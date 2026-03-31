# models/product_image.py

from sqlalchemy import Column, Integer, ForeignKey, LargeBinary, String
from sqlalchemy.orm import relationship
from database.db import Base


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, index=True)

    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))

    image_data = Column(LargeBinary, nullable=False)     
    content_type = Column(String, default="image/webp")  
    filename = Column(String, nullable=True)              
    position = Column(Integer, default=0)                 

    product = relationship("Product", back_populates="images") 
