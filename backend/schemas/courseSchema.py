from pydantic import BaseModel, Field
from typing import Optional,List
from datetime import datetime

class CourseCreate(BaseModel):
    title: str = Field(..., min_length=3)
    description: str

class CourseResponse(BaseModel):
    id: str
    title: str
    description: str
    thumbnail: str
    teacher_id: str
    created_at: datetime




class CourseListResponse(BaseModel):
    """Response model for list of courses with pagination info"""
    courses: List[CourseResponse]
    total: int = Field(description="Total number of courses")
    skip: int = Field(description="Number of courses skipped")
    limit: int = Field(description="Maximum courses returned")
    
    class Config:
        from_attributes = True