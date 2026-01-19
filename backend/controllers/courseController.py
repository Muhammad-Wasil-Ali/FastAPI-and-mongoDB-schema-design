from models.courseModel import Course
from schemas.courseSchema import CourseResponse,CourseUpdateResponse,DeleteCourseResponse
from fastapi import HTTPException, status
import cloudinary.uploader
# controllers/courseController.py
from datetime import datetime
from beanie import PydanticObjectId
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
        
        courses = await Course.find().skip(skip).limit(limit).to_list()
        print(f"✅ Found {len(courses)} courses")
        print("\n" + "=" * 60 + "\n")
        
        for index, course in enumerate(courses, 1):
            print(f"\n📚 Course {index}:")
            print(f"   ID: {course.id}")
            print(f"   Title: {course.title}")
            print(f"   Teacher Link: {course.teacher}")
            print(f"   Teacher ID: {course.teacher.ref.id}")
            
            print(f"   Teacher Collection: {course.teacher.ref.collection}")
        
        print("\n" + "=" * 60 + "\n")
        return [
            CourseResponse(
                id=str(course.id),
                title=course.title,
                description=course.description,
                thumbnail=course.thumbnail,
                teacher_id=str(course.teacher.ref.id),
                created_at=course.created_at
            )
            for course in courses
        ]
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to fetch courses: {str(e)}")
    
    
    
    




# ... your existing controllers ...

async def updateCourseController(
    course_id: str,
    title: str = None,
    description: str = None,
    thumbnail = None,
    current_user_id: str = None
):
    """Update a course - simple version"""
    try:
        print(f"🔄 Updating course {course_id}")
        
        # 1️⃣ Find the course
        course = await Course.get(PydanticObjectId(course_id))
        
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        print(f"✅ Course found: {course.title}")
        
        # 2️⃣ Check if user is the owner
        if str(course.teacher.ref.id) != current_user_id:
            raise HTTPException(
                status_code=403, 
                detail="You can only update your own courses"
            )
        
        print(f"✅ User authorized to update")
        
        # 3️⃣ Update title if provided
        if title:
            if len(title.strip()) < 3:
                raise HTTPException(
                    status_code=400,
                    detail="Title must be at least 3 characters"
                )
            course.title = title.strip()
            print(f"📝 Title updated to: {course.title}")
        
        # 4️⃣ Update description if provided
        if description:
            if len(description.strip()) < 10:
                raise HTTPException(
                    status_code=400,
                    detail="Description must be at least 10 characters"
                )
            course.description = description.strip()
            print(f"📝 Description updated")
        
        # 5️⃣ Update thumbnail if provided
        if thumbnail:
            print(f"🖼️ Uploading new thumbnail...")
            
            # Validate file
            allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
            if thumbnail.content_type not in allowed_types:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid file type"
                )
            
            # Check size
            file_bytes = await thumbnail.read()
            if len(file_bytes) > 5 * 1024 * 1024:
                raise HTTPException(
                    status_code=400,
                    detail="File too large (max 5MB)"
                )
            
            # Upload to Cloudinary
            try:
                import io
                upload_result = cloudinary.uploader.upload(
                    io.BytesIO(file_bytes),
                    folder="courses"
                )
                course.thumbnail = upload_result["secure_url"]
                print(f"✅ Thumbnail updated: {course.thumbnail}")
            except Exception as e:
                print(f"❌ Upload error: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Thumbnail upload failed: {str(e)}"
                )
        
        # 6️⃣ Set updated_at timestamp
        course.updated_at = datetime.utcnow()
        
        # 7️⃣ Save to database
        await course.save()
        print(f"✅ Course saved successfully")
        
        # 8️⃣ Return response
        return CourseUpdateResponse(
            id=str(course.id),
            title=course.title,
            description=course.description,
            thumbnail=course.thumbnail,
            teacher_id=str(course.teacher.ref.id),
            created_at=course.created_at,
            updated_at=course.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update course: {str(e)}"
        )
        
        




# ... your existing controllers ...

async def deleteCourseController(course_id: str, current_user_id: str):
    """Delete a course - simple version"""
    try:
        print(f"🗑️ Deleting course {course_id}")
        
        # 1️⃣ Find the course
        course = await Course.get(PydanticObjectId(course_id))
        
        if not course:
            raise HTTPException(
                status_code=404,
                detail="Course not found"
            )
        
        print(f"✅ Course found: {course.title}")
        
        # 2️⃣ Check if user is the owner
        if str(course.teacher.ref.id) != current_user_id:
            raise HTTPException(
                status_code=403,
                detail="You can only delete your own courses"
            )
        
        print(f"✅ User authorized to delete")
        
        # 3️⃣ Delete thumbnail from Cloudinary (optional but recommended)
        try:
            if "cloudinary.com" in course.thumbnail:
                # Extract public_id from URL
                # URL format: https://res.cloudinary.com/cloud_name/image/upload/v123456/courses/filename.jpg
                url_parts = course.thumbnail.split("/")
                
                # Find 'courses' folder and get filename
                if "courses" in url_parts:
                    idx = url_parts.index("courses")
                    filename = url_parts[-1].split(".")[0]  # Remove extension
                    public_id = f"courses/{filename}"
                    
                    print(f"🗑️ Deleting thumbnail: {public_id}")
                    cloudinary.uploader.destroy(public_id)
                    print(f"✅ Thumbnail deleted from Cloudinary")
        except Exception as e:
            # Don't fail if cloudinary delete fails
            print(f"⚠️ Warning: Could not delete thumbnail: {str(e)}")
        
        # 4️⃣ Store info before deleting
        course_title = course.title
        course_id_str = str(course.id)
        
        # 5️⃣ Delete course from database
        await course.delete()
        print(f"✅ Course deleted from database")
        
        # 6️⃣ Return success response
        return DeleteCourseResponse(
            message="Course deleted successfully",
            deleted_course_id=course_id_str,
            deleted_course_title=course_title
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete course: {str(e)}"
        )