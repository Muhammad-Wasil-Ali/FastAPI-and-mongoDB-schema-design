from fastapi import APIRouter
from schemas.userSchema import UserCreate,UserResponse
from controllers.userController import createUserController

router=APIRouter(prefix="/api/v1/user",tags=["Auth"])

@router.post("/signup",response_model=UserResponse)
async def signup(user:UserCreate):
    return await createUserController(user)