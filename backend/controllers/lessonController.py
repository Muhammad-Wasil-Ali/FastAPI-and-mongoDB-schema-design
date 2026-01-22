import os
import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, UploadFile
from models.lessonModel import Lesson
from models.courseModel import Course
from beanie import PydanticObjectId
from typing import List
import traceback

# Configure Cloudinary (make sure you have this in your config)
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# Create videos folder if it doesn't exist
VIDEOS_FOLDER = "videos"
os.makedirs(VIDEOS_FOLDER, exist_ok=True)


async def createLessonController(course_id: str, video: UploadFile, teacher_id: str):
    """Create a new lesson with video upload"""
    
    try:
        # Validate course exists
        course = await Course.get(PydanticObjectId(course_id))
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
       
        # Check if current user is the course owner
        if str(course.teacher.ref.id) != teacher_id:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to add lessons to this course"
            )
        
        # Generate unique filename
        import uuid
        file_extension = video.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        local_file_path = os.path.join(VIDEOS_FOLDER, unique_filename)
        
       # Save video to local folder first
        content = await video.read()
        with open(local_file_path, 'wb') as out_file:
            out_file.write(content)
        
        # Upload to Cloudinary
        try:
            upload_result = cloudinary.uploader.upload(
                local_file_path,
                resource_type="video",
                folder="lip_learn_lessons"
            )
            cloudinary_url = upload_result["secure_url"]
        except Exception as e:
            # If cloudinary upload fails, delete local file
            if os.path.exists(local_file_path):
                os.remove(local_file_path)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload video to Cloudinary: {str(e)}"
            )
        print("file name ",unique_filename)
        print("file url ",cloudinary_url)
        print("file id ",course)
        
        # Create lesson in database
        lesson = Lesson(
            course_id=course.id,
            video_name=unique_filename,
            video_url=cloudinary_url
        )
        print("file name ",unique_filename)
        print("file url ",cloudinary_url)
        print("file id ",course.id)
        await lesson.insert()
        print("file name ",unique_filename)
        print("file url ",cloudinary_url)
        print("file id ",course.id)
        return {
            "id": str(lesson.id),
            "course_id": str(lesson.course_id.ref.id),
            "video_name": lesson.video_name,
            "video_url": lesson.video_url,
            "created_at": lesson.created_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in createLessonController: {str(e)}")
        print(traceback.format_exc())  # This prints full error traceback
        raise HTTPException(status_code=500, detail="Failed to create lesson")


async def getAllLessonsController(course_id: str, skip: int = 0, limit: int = 10):
    """Get all lessons for a specific course"""
    
    try:
        # Validate course exists
        print(f"Searching for course_id: {course_id}")
        course = await Course.get(PydanticObjectId(course_id))
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        print(f"Course found: {course.id}")
        
        # Fetch lessons - Try different query methods
        # Method 1: Query by reference ID
        # lessons = await Lesson.find(
        #     Lesson.course_id.ref.id == PydanticObjectId(course_id)
        # ).skip(skip).limit(limit).to_list()
        
        # If Method 1 doesn't work, try Method 2:
        lessons = await Lesson.find(
            {"course_id.$id": PydanticObjectId(course_id)}
        ).skip(skip).limit(limit).to_list()
        
        print(f"Found {len(lessons)} lessons")
       
        
        # Debug: Print all lessons in database
        all_lessons = await Lesson.find_all().to_list()
        print(f"Total lessons in DB: {len(all_lessons)}")
        for l in all_lessons:
            print(f"Lesson course_id type: {type(l.course_id)}, value: {l.course_id}")
        
        return [
            {
                "id": str(lesson.id),
                "course_id": str(lesson.course_id.ref.id),
                "video_name": lesson.video_name,
                "video_url": lesson.video_url,
                "created_at": lesson.created_at
            }
            for lesson in lessons
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in getAllLessonsController: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to fetch lessons")

async def updateLessonController(lesson_id: str, video: UploadFile, current_user_id: str):
    """Update a lesson's video"""
    
    try:
        # Get lesson
        lesson = await Lesson.get(PydanticObjectId(lesson_id))
        if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")
        
        # Get course to verify ownership
        course = await Course.get(lesson.course_id.ref.id)
        if str(course.teacher_id.ref.id) != current_user_id:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to update this lesson"
            )
        
        # Store old video info for cleanup
        old_video_name = lesson.video_name
        old_video_url = lesson.video_url
        
        # Generate unique filename
        import uuid
        file_extension = video.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        local_file_path = os.path.join(VIDEOS_FOLDER, unique_filename)
        
        # Save new video to local folder
        content = await video.read()
        with open(local_file_path, 'wb') as out_file:
            out_file.write(content)
        
        # Upload to Cloudinary
        try:
            upload_result = cloudinary.uploader.upload(
                local_file_path,
                resource_type="video",
                folder="lip_learn_lessons"
            )
            cloudinary_url = upload_result["secure_url"]
        except Exception as e:
            if os.path.exists(local_file_path):
                os.remove(local_file_path)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload video to Cloudinary: {str(e)}"
            )
        
        # Update lesson
        lesson.video_name = unique_filename
        lesson.video_url = cloudinary_url
        await lesson.save()
        
        # Delete old video from local folder
        old_local_path = os.path.join(VIDEOS_FOLDER, old_video_name)
        if os.path.exists(old_local_path):
            os.remove(old_local_path)
        
        # Delete old video from Cloudinary
        try:
            # Extract public_id from old URL
            public_id = old_video_url.split("/")[-1].split(".")[0]
            cloudinary.uploader.destroy(f"lip_learn_lessons/{public_id}", resource_type="video")
        except:
            pass  # If deletion fails, just continue
        
        return {
            "id": str(lesson.id),
            "course_id": str(lesson.course_id.ref.id),
            "video_name": lesson.video_name,
            "video_url": lesson.video_url,
            "created_at": lesson.created_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in updateLessonController: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update lesson")


async def deleteLessonController(lesson_id: str, current_user_id: str):
    """Delete a lesson"""
    
    try:
        # Get lesson
        lesson = await Lesson.get(PydanticObjectId(lesson_id))
        if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")
        
        # Get course to verify ownership
        course = await Course.get(lesson.course_id.ref.id)
        if str(course.teacher_id.ref.id) != current_user_id:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to delete this lesson"
            )
        
        video_name = lesson.video_name
        video_url = lesson.video_url
        
        # Delete from database
        await lesson.delete()
        
        # Delete from local folder
        local_path = os.path.join(VIDEOS_FOLDER, video_name)
        if os.path.exists(local_path):
            os.remove(local_path)
        
        # Delete from Cloudinary
        try:
            public_id = video_url.split("/")[-1].split(".")[0]
            cloudinary.uploader.destroy(f"lip_learn_lessons/{public_id}", resource_type="video")
        except:
            pass
        
        return {
            "message": "Lesson deleted successfully",
            "deleted_lesson_id": str(lesson_id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in deleteLessonController: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete lesson")