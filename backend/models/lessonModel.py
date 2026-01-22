from beanie import Document, Link
from datetime import datetime
from models.courseModel import Course
class Lesson(Document):
    course_id: Link[Course]
    video_name: str  # Filename in videos folder
    video_url: str   # Cloudinary URL
    created_at: datetime = datetime.utcnow()
    
    class Settings:
        name = "lessons"