from typing import Optional
from datetime import datetime
from enum import Enum

from beanie import Document
from pydantic import Field


class UserRole(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"


class User(Document):
    email:str
    password: str
    role: UserRole
    first_name: str
    last_name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"  # MongoDB collection name
