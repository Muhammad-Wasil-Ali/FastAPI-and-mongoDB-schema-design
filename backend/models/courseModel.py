from beanie import Document, Link
from pydantic import Field
from datetime import datetime
from models.userModel import User

class Course(Document):
    title: str = Field(min_length=3, max_length=100)
    description: str = Field(min_length=10, max_length=500)
    thumbnail: str  # ✅ Required now
    teacher: Link[User]  # 🔐 Always set from token, not client
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "courses"
