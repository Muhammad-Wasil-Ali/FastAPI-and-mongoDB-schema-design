from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI
from models.userModel import User
from models.courseModel import Course
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI=os.getenv("MONGO_URI")
dbName="LipLearn"

if not MONGO_URI:
    raise RuntimeError("Mongo Uri is not set correctly")

client=AsyncIOMotorClient(MONGO_URI)

async def connectDB():
    
    try:
        
       await init_beanie(
            database=client[dbName],
            document_models=[User,Course]
            )
       print("Mongo db connected successfully")
    except Exception as e:
        print("Mongodb connection failed ",str(e))
        raise