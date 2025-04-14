from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean, Time
from sqlalchemy.orm import relationship
from database import Base



class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)  
    specialization = Column(String(255))    
    phone = Column(String(20))              
    image_filename = Column(String(512))    # Changed from imageUrl to image_filename

    visits = relationship("Visit", back_populates="doctor")
  


# Visit Model
class Visit(Base):
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    doctor_id = Column(Integer, ForeignKey("doctors.id"))

    doctor = relationship("Doctor", back_populates="visits")
    patients = relationship("Patient", back_populates="visit")

# Patient Model
class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)  
    contact = Column(String(20))            
    fee_status = Column(String(50), default="due")  
    visit_id = Column(Integer, ForeignKey("visits.id"))
    serial_no = Column(Integer)

    visit = relationship("Visit", back_populates="patients")

# models.py (create or update)
class DoctorSchedule(Base):
    __tablename__ = "doctor_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    specialization = Column(String, nullable=False)
    image_filename = Column(String, nullable=True)
    contact_number = Column(String, nullable=True)
    day_of_week = Column(String)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_available = Column(Boolean, default=True)
    specific_date = Column(Date, nullable=True)

class GalleryImage(Base):
    __tablename__ = "gallery_images"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    description = Column(String(255))
    image_url = Column(String(255), nullable=False)
    order_index = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

   
