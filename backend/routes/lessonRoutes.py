from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException, Query, Path
from schemas.lessonSchema import LessonResponse, LessonUpdateResponse, DeleteLessonResponse
from controllers.lessonController import createLessonController, getAllLessonsController, updateLessonController, deleteLessonController
from dependencies.auth import require_teacher
from typing import List,Optional

router = APIRouter(prefix="/api/v1/lesson", tags=["Lesson"])

@router.post("/create", response_model=LessonResponse, status_code=201)
async def create_lesson(
    course_id: str = Form(...),
    video: UploadFile = File(...),
    current_user = Depends(require_teacher)
):
    """
    Create a new lesson with video upload
    - Requires teacher authentication
    - Uploads video to local folder then Cloudinary
    - Saves lesson to MongoDB
    """
    
    # Validate file type
    allowed_types = ["video/mp4", "video/mpeg", "video/quicktime", "video/x-msvideo", "video/webm"]
    if video.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. Only MP4, MPEG, MOV, AVI, and WebM videos are allowed"
        )
   
    # Validate file size (max 50MB)
    contents = await video.read()
    if len(contents) > 50 * 1024 * 1024:
        raise HTTPException(
            status_code=400, 
            detail="File too large. Maximum size is 50MB"
        )
    
    # Reset file pointer
    await video.seek(0)
    
    try:
        # Call controller
        lesson = await createLessonController(
            course_id=course_id,
            video=video,
            teacher_id=str(current_user['id'])
        )
        return lesson
    
    except HTTPException as he:
        raise he
    
    except Exception as e:
        print(f"Error creating lesson: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while creating the lesson"
        )


@router.get("/course/{course_id}", response_model=List[LessonResponse])
async def get_all_lessons(
    course_id: str = Path(..., description="Course ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """Get all lessons for a specific course with pagination"""
    try:
        lessons = await getAllLessonsController(course_id=course_id, skip=skip, limit=limit)
        return lessons
    except Exception as e:
        print(f"Error fetching lessons: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch lessons")


@router.put("/{lesson_id}", response_model=LessonUpdateResponse)
async def update_lesson(
    lesson_id: str = Path(..., description="Lesson ID"),
    video: Optional[UploadFile] = File(None),
    current_user = Depends(require_teacher)
):
    """
    Update a lesson
    - Only course owner can update
    - Video is optional
    """
    
    if not video:
        raise HTTPException(
            status_code=400,
            detail="Provide a video to update"
        )
    
    # Validate file type if video provided
    if video:
        allowed_types = ["video/mp4", "video/mpeg", "video/quicktime", "video/x-msvideo", "video/webm"]
        if video.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail="Invalid file type. Only MP4, MPEG, MOV, AVI, and WebM videos are allowed"
            )
    
    try:
        updated_lesson = await updateLessonController(
            lesson_id=lesson_id,
            video=video,
            current_user_id=str(current_user['id'])
        )
        return updated_lesson
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update lesson"
        )


@router.delete("/{lesson_id}", response_model=DeleteLessonResponse, status_code=200)
async def delete_lesson(
    lesson_id: str = Path(..., description="Lesson ID to delete"),
    current_user = Depends(require_teacher)
):
    """
    Delete a lesson
    - Only course owner can delete
    - Also deletes video from Cloudinary
    """
    
    try:
        result = await deleteLessonController(
            lesson_id=lesson_id,
            current_user_id=str(current_user['id'])
        )
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete lesson"
        )