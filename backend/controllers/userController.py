from models.userModel import User
from schemas.userSchema import UserCreate,UserResponse,UserLogin
from fastapi import status,HTTPException
from passlib.hash import bcrypt
from utils.security import create_access_token,verify_access_token
from fastapi import Response

# password_context=CryptContext(
#     schemes=["bcrypt"],deprecated="auto"
# )
# //user signup

async def createUserController(body:UserCreate)->UserResponse:
    
    existingUser=await User.find_one(User.email==body.email)
    
    if existingUser:
        raise ValueError("User with this email already exist")
    
    # password hashing
    hashedPassword=bcrypt.hash(body.password)
    print(body.password)
    print(hashedPassword)
    user=User(email=body.email,password=hashedPassword,first_name=body.first_name,last_name=body.last_name,role=body.role)
    print("Before saving in databse : ",user)
    await user.insert()
    print("after saving in database : ",user)

    return UserResponse(
        id=str(user.id),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        created_at=user.created_at
    )
    
    
    
# login controller

async def loginController(body: UserLogin,response:Response):
    # 1. Find user by email
    user = await User.find_one(User.email == body.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    # 2. Verify password
    if not bcrypt.verify(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    # 3. Create JWT token
    token = create_access_token({"id": str(user.id), "role": user.role})

    # 4. Set token in HTTP-only cookie
    response.set_cookie(
        key="access_token",       # cookie name
        value=token,              # JWT token
        httponly=True,            # not accessible via JS
        max_age=60*60,            # 1 hour in seconds
        secure=False,             # True if HTTPS, False if dev HTTP
        samesite="lax"            # protects against CSRF
    )

    # 5. Return success response (excluding password)
    return {
        "success": True,
        "message": "Login successful",
        "data": {
            "id": str(user.id),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "role": user.role
        }
    }

   