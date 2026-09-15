from database import Base
from sqlalchemy import Column, String, Integer, Boolean, Date, DateTime, ForeignKey


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True )
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True,nullable=False)
    phone = Column(String,nullable=False)
    dob = Column(Date, nullable=False)

    password_hash = Column(String,nullable=False)

    role = Column(String, nullable=False, default="student")
    subject = Column(String, nullable=True)
    standard = Column(String, nullable=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    email_verified = Column(Boolean,default=False)
    must_change_password = Column(Boolean, default=False)

    otp = Column(String,nullable=True)
    otp_expiry = Column(DateTime , nullable=True)

   
