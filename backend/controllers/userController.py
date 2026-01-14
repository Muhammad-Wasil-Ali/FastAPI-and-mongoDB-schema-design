from models.userModel import User
from schemas.userSchema import UserCreate,UserResponse

from passlib.hash import bcrypt

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
    print("Before saving in dayabse : ",user)
    await user.insert()
    print("after saving in dayabse : ",user)

    return UserResponse(
        id=str(user.id),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        created_at=user.created_at
    )