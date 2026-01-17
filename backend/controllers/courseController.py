from models.courseModel import Course
from schemas.courseSchema import CourseResponse
from fastapi import HTTPException, status
import cloudinary.uploader

async def createCourseController(title: str, description: str, thumbnail, teacher_id: str):
    # 1️⃣ Upload image to Cloudinary
    print("=" * 50)
    print("here is metadata in controller", title, description)
    print("Thumbnail object:", thumbnail)
    print("Thumbnail file:", thumbnail.file)
    print("Thumbnail filename:", thumbnail.filename)
    print("Thumbnail content_type:", thumbnail.content_type)
    print("=" * 50)
    
    try:
        print("☁️ Attempting Cloudinary upload...")
        upload_result = cloudinary.uploader.upload(thumbnail.file)
        thumbnail_url = upload_result["secure_url"]
        print(f"✅ Upload successful: {thumbnail_url}")
        
    except Exception as e:
        # 👇 THIS IS THE KEY - PRINT THE ACTUAL ERROR
        print(f"❌ Cloudinary Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()  # This shows the full error
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")

    # 2️⃣ Create course document
    course = Course(
        title=title,
        description=description,
        thumbnail=thumbnail_url,
        teacher=teacher_id
    )

    # 3️⃣ Save to MongoDB
    await course.insert()

    # 4️⃣ Return response
    return CourseResponse(
        id=str(course.id),
        title=course.title,
        description=course.description,
        thumbnail=course.thumbnail,
        teacher_id=str(course.teacher),
        created_at=course.created_at
    )
    
    
    


# controllers/courseController.py
async def getAllCoursesController(skip: int = 0, limit: int = 10):
    """Get all courses with pagination"""
    try:
        print(f"📚 Fetching courses (skip={skip}, limit={limit})")
        
        courses = await Course.find_all().skip(skip).limit(limit).to_list()
        print(f"✅ Found {len(courses)} courses")
        
        return [
            CourseResponse(
                id=str(course.id),
                title=course.title,
                description=course.description,
                thumbnail=course.thumbnail,
                teacher_id=course.teacher,
                created_at=course.created_at
            )
            for course in courses
        ]
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to fetch courses: {str(e)}")