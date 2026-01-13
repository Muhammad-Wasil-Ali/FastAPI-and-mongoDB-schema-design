from pydantic import BaseModel,EmailStr,Field
from enum import Enum
from datetime import datetime
class UserRole(str,Enum):
    STUDENT="student"
    TEACHER="teacher"

class UserCreate(BaseModel):
    first_name:str=Field(min_length=3,max_length=20)
    last_name:str=Field(min_length=3,max_length=20)
    email:EmailStr
    password:str=Field(min_length=6)
    role:UserRole.TEACHER
    
    

class UserResponse(BaseModel):
    first_name:str
    last_name:str
    email:EmailStr
    role:UserRole
    created_at:datetime