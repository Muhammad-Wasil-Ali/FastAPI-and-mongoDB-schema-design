from typing import Optional
from datetime import datetime
from enum import Enum
from pydantic import EmailStr,Field
from beanie import Document



class UserRole(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"


class User(Document):
    email:EmailStr
    password: str=Field(min_length=6)
    role: UserRole
    first_name: str=Field(min_length=3,max_length=20)
    last_name: str=Field(min_length=3,max_length=20)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"  # MongoDB collection name
