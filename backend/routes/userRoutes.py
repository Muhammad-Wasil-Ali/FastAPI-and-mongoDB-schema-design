from fastapi import APIRouter,Response
from schemas.userSchema import UserCreate,UserResponse,UserLogin
from controllers.userController import createUserController,loginController

router=APIRouter(prefix="/api/v1/user",tags=["Auth"])

@router.post("/signup",response_model=UserResponse)
async def signup(user:UserCreate):
    return await createUserController(user)


@router.post("/login")
async def login(user:UserLogin,response:Response):
    return await loginController(user,response)