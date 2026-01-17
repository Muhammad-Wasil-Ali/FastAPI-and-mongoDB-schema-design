from fastapi import FastAPI
from config.database import connectDB  # your DB connection function
# Optional: import routers when you have them

from routes.userRoutes import router as user_router
from routes.courseRoutes import router as course_router
from utils.cloudinary import configure_cloudinary

# Configure Cloudinary when app starts
configure_cloudinary()
# Create FastAPI app (like express())
app = FastAPI(
    title="LipLearn API",
    version="1.0.0"
)

# MongoDB startup hook
@app.on_event("startup")
async def start_db():
    await connectDB()

# Health check route
@app.get("/")
async def root():
    return {"status": "API is running"}

# Include routers (like Express routes) when ready
app.include_router(user_router)
app.include_router(course_router)
# app.include_router(task_router)
