from sqlalchemy import Column,Integer,String,Boolean,DateTime
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True,index=True)
    username = Column(String,nullable=False, unique=True,index=True)
    email = Column(String,nullable=False, unique=True)
    hash_pass = Column(String,nullable=False)
    is_active = Column(Boolean,default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    role = Column(String, nullable=False )