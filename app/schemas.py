from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional


class UserCreate(BaseModel):
    username:str
    email:str
    password: str

class UserLogin(BaseModel):
    email:str
    password:str
    
class UserResponse(BaseModel):
    id :int
    username: str
    email:str
    is_active :bool
    created_at: datetime
    model_config=ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None

class PasswordChange(BaseModel):
    old_password:str
    new_password:str