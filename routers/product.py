from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import Response
from sqlalchemy.orm import Session, joinedload
from database.db import get_db
from models.product import Product
from models.product_image import ProductImage
from models.user import UserRole, User
from schemas.product import ProductCreate, ProductUpdate, ProductResponse
from core.security import get_current_user
from io import BytesIO
from PIL import Image

router = APIRouter(prefix="/product", tags=["Product"])

MAX_IMAGES_PER_PRODUCT = 5
MAX_IMAGE_SIZE = 800  # Max width/height in pixels
WEBP_QUALITY = 80  # Compression quality (1-100)


def compress_image(file_bytes: bytes, filename: str = "") -> tuple[bytes, str]:
    """Compress and convert image to WebP format."""
    try:
        img = Image.open(BytesIO(file_bytes))

        # Convert RGBA to RGB (WebP supports RGBA but JPEG doesn't)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # Resize if too large (maintain aspect ratio)
        if img.width > MAX_IMAGE_SIZE or img.height > MAX_IMAGE_SIZE:
            img.thumbnail((MAX_IMAGE_SIZE, MAX_IMAGE_SIZE), Image.Resampling.LANCZOS)

        # Compress to WebP
        output = BytesIO()
        img.save(output, format="WEBP", quality=WEBP_QUALITY, optimize=True)
        compressed_bytes = output.getvalue()

        return compressed_bytes, "image/webp"

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")


# ✅ Add Product (Farmer Only)
@router.post("/add", response_model=ProductResponse)
def add_product(data: ProductCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] != "farmer":
        raise HTTPException(status_code=403, detail="Only farmers can add products")

    product = Product(
        name=data.name,
        description=data.description,
        price=data.price,
        stock=data.stock,
        farmer_id=current_user["user_id"]
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


# ✅ Upload Images (Farmer Only, max 5)
@router.post("/{product_id}/images", response_model=ProductResponse)
async def upload_product_images(
    product_id: int,
    files: list[UploadFile] = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    product = db.query(Product).options(joinedload(Product.images)).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if current_user["role"] != "farmer" or product.farmer_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not allowed")

    # Check how many images already exist
    existing_count = len(product.images)
    if existing_count + len(files) > MAX_IMAGES_PER_PRODUCT:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {MAX_IMAGES_PER_PRODUCT} images allowed. Currently {existing_count} images exist."
        )

    # Validate file types
    allowed_types = {"image/jpeg", "image/png", "image/webp", "image/gif", "image/bmp"}
    for f in files:
        if f.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail=f"Invalid file type: {f.content_type}. Allowed: JPEG, PNG, WebP, GIF, BMP")

    # Process and store each image
    for i, f in enumerate(files):
        file_bytes = await f.read()

        if len(file_bytes) > 10 * 1024 * 1024:  # 10MB limit per file
            raise HTTPException(status_code=400, detail=f"File {f.filename} is too large (max 10MB)")

        compressed_data, content_type = compress_image(file_bytes, f.filename)

        img = ProductImage(
            product_id=product_id,
            image_data=compressed_data,
            content_type=content_type,
            filename=f.filename,
            position=existing_count + i
        )
        db.add(img)

    db.commit()
    db.refresh(product)

    return product


# ✅ Serve Image (Public)
@router.get("/image/{image_id}")
def get_product_image(image_id: int, db: Session = Depends(get_db)):
    img = db.query(ProductImage).filter(ProductImage.id == image_id).first()
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")

    return Response(
        content=img.image_data,
        media_type=img.content_type,
        headers={
            "Cache-Control": "public, max-age=86400",  # Cache 1 day
            "Content-Disposition": f"inline; filename=\"product_{img.product_id}_{img.position}.webp\""
        }
    )


# ✅ Delete Image (Farmer Only)
@router.delete("/image/{image_id}")
def delete_product_image(image_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    img = db.query(ProductImage).filter(ProductImage.id == image_id).first()
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")

    product = db.query(Product).filter(Product.id == img.product_id).first()
    if current_user["role"] != "farmer" or product.farmer_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not allowed")

    db.delete(img)
    db.commit()
    return {"message": "Image deleted"}


# ✅ Update Product
@router.put("/update/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, data: ProductUpdate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if current_user["role"] != "farmer" or product.farmer_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not allowed to update this product")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product


# ✅ Delete Product
@router.delete("/delete/{product_id}")
def delete_product(product_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if current_user["role"] != "farmer" or product.farmer_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not allowed to delete this product")

    db.delete(product)
    db.commit()
    return {"message": "Product deleted"}


# ✅ List Products (Public)
@router.get("/list", response_model=list[ProductResponse])
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).options(joinedload(Product.images)).filter(Product.status == "available").all()