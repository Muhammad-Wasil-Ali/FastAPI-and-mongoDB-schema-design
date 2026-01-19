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
  
    courses: List[CourseResponse]
    total: int = Field(description="Total number of courses")
    skip: int = Field(description="Number of courses skipped")
    limit: int = Field(description="Maximum courses returned")
    
    class Config:
        from_attributes = True
    
    
class CourseUpdateResponse(BaseModel):
    """Response after updating a course"""
    id: str
    title: str
    description: str
    thumbnail: str
    teacher_id: str
    created_at: datetime
   
    
    class Config:
        from_attributes = True
        


class DeleteCourseResponse(BaseModel):
    """Response after deleting a course"""
    message: str
    deleted_course_id: str
    deleted_course_title: str