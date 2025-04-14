from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import models
import schemas
from database import get_db
import shutil
import os
from datetime import datetime
from fastapi.responses import FileResponse

router = APIRouter(
    prefix="/gallery",
    tags=["gallery"]
)

# Configure upload directory
UPLOAD_DIR = "uploads/gallery"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/", response_model=List[schemas.GalleryImageResponse])
def get_gallery_images(
    skip: int = 0, 
    limit: int = 100, 
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """
    Get all gallery images
    """
    query = db.query(models.GalleryImage)
    if active_only:
        query = query.filter(models.GalleryImage.is_active == True)
    
    # Order by order_index
    query = query.order_by(models.GalleryImage.order_index)
    
    images = query.offset(skip).limit(limit).all()
    return images

@router.get("/{image_id}", response_model=schemas.GalleryImageResponse)
def get_gallery_image(image_id: int, db: Session = Depends(get_db)):
    """
    Get a specific gallery image by ID
    """
    image = db.query(models.GalleryImage).filter(models.GalleryImage.id == image_id).first()
    if image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return image

@router.post("/", response_model=schemas.GalleryImageResponse, status_code=status.HTTP_201_CREATED)
async def create_gallery_image(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    order_index: int = Form(0),
    is_active: bool = Form(True),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a new gallery image (admin only)
    """
    # Validate file type
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Create unique filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_extension = os.path.splitext(image.filename)[1]
    new_filename = f"{timestamp}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, new_filename)
    
    # Save uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    
    # Create database entry
    db_image = models.GalleryImage(
        title=title,
        description=description,
        image_url=f"/uploads/gallery/{new_filename}",  # URL path to file
        order_index=order_index,
        is_active=is_active
    )
    
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    
    return db_image

@router.put("/{image_id}", response_model=schemas.GalleryImageResponse)
def update_gallery_image(
    image_id: int,
    image: schemas.GalleryImageUpdate,
    db: Session = Depends(get_db)
):
    """
    Update gallery image details (admin only)
    """
    db_image = db.query(models.GalleryImage).filter(models.GalleryImage.id == image_id).first()
    if db_image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Update fields
    for key, value in image.dict(exclude_unset=True).items():
        setattr(db_image, key, value)
    
    db.commit()
    db.refresh(db_image)
    return db_image

@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_gallery_image(image_id: int, db: Session = Depends(get_db)):
    """
    Delete a gallery image (admin only)
    """
    db_image = db.query(models.GalleryImage).filter(models.GalleryImage.id == image_id).first()
    if db_image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Get file path from URL
    file_name = os.path.basename(db_image.image_url)
    file_path = os.path.join(UPLOAD_DIR, file_name)
    
    # Remove file if it exists
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Remove database entry
    db.delete(db_image)
    db.commit()
    
    return None