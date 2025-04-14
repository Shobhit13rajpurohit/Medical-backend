from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import models
from database import engine
from routers import doctors
from routers import gallery
from routers import patients
from routers import schedules
from routers import visits


# Create tables in the database
models.Base.metadata.create_all(bind=engine)

# Create upload directories if they don't exist
os.makedirs("uploads/doctor_images", exist_ok=True)
os.makedirs("uploads/gallery", exist_ok=True)
os.makedirs("uploads/doctors", exist_ok=True)

# Initialize FastAPI app
app = FastAPI(
    title="Medical Services API",
    description="API for managing doctors, patients, visits, schedules, and gallery",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for serving uploads
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(doctors.router)
app.include_router(patients.router)
app.include_router(visits.router)
app.include_router(schedules.router)
app.include_router(gallery.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Medical Services API"}

# Run the application with: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)