from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CourseCreate(BaseModel):
    title: str = Field(..., min_length=3)
    description: str
   
    
    
    



class CourseResponse(BaseModel):
    id: str
    title: str
    description: str
    thumbnail: str  # path or URL
    teacher_id: str
    created_at: datetime

