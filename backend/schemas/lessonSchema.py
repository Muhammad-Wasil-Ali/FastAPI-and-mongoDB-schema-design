from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class LessonCreate(BaseModel):
    course_id: str
    # video will be uploaded as UploadFile in the route

class LessonResponse(BaseModel):
    id: str
    course_id: str
    video_name: str  # Filename stored in videos folder
    video_url: str   # Cloudinary URL
    created_at: datetime
    
    class Config:
        from_attributes = True

class LessonUpdateResponse(BaseModel):
    """Response after updating a lesson"""
    id: str
    course_id: str
    video_name: str
    video_url: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class DeleteLessonResponse(BaseModel):
    """Response after deleting a lesson"""
    message: str
    deleted_lesson_id: str