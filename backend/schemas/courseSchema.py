from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CourseCreate(BaseModel):
    title: str = Field(..., min_length=3)
    description: str
    thumbnail: str  # required
    
    
    



class CourseResponse(BaseModel):
    id: str
    title: str
    description: str
    thumbnail: str
    teacher: str  # teacher user id
    created_at: datetime
