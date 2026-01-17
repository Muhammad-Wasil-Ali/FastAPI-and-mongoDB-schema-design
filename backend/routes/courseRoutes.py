from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException
from schemas.courseSchema import CourseResponse
from controllers.courseController import createCourseController,getAllCoursesController
from dependencies.auth import require_teacher
from typing import List
router = APIRouter(prefix="/api/v1/course", tags=["Course"])

@router.post("/create", response_model=CourseResponse, status_code=201)
async def create_course(
    title: str = Form(...),
    description: str = Form(...),
    thumbnail: UploadFile = File(...),
    current_user = Depends(require_teacher)
):
    """
    Create a new course with thumbnail upload
    - Requires teacher authentication
    - Uploads thumbnail to Cloudinary
    - Saves course to MongoDB
    """
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
    if thumbnail.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. Only JPEG, PNG, and WebP images are allowed"
        )
   
    # Validate file size (max 5MB)
    contents = await thumbnail.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=400, 
            detail="File too large. Maximum size is 5MB"
        )
    
    # Reset file pointer
    await thumbnail.seek(0)
    
    # Validate title length
    if len(title.strip()) < 3:
        raise HTTPException(
            status_code=400,
            detail="Title must be at least 3 characters long"
        )
    
    if len(title) > 200:
        raise HTTPException(
            status_code=400,
            detail="Title must not exceed 200 characters"
        )
    
    # Validate description
    if len(description.strip()) < 10:
        raise HTTPException(
            status_code=400,
            detail="Description must be at least 10 characters long"
        )
    
    try:
        
        
        # Call controller
        course = await createCourseController(
            title=title.strip(),
            description=description.strip(),
            thumbnail=thumbnail,
            teacher_id=str(current_user['id'])  # or current_user["id"] depending on your auth
        )
        return course
    
    except HTTPException as he:
        # Re-raise HTTP exceptions from controller
        raise he
    
    except Exception as e:
        # Log the error (use proper logging in production)
        print(f"Error creating course: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while creating the course"
        )
        
        
# routes/courseRoute.py
@router.get("/all", response_model=List[CourseResponse])
async def get_all_courses(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """Get all courses with pagination"""
    try:
        courses = await getAllCoursesController(skip=skip, limit=limit)
        return courses
    except Exception as e:
        print(f"Error fetching courses: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch courses")