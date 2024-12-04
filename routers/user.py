import random
import string
from os import getenv

import bcrypt
from bson import ObjectId
from fastapi import APIRouter, Request
from fastapi import HTTPException
from dotenv import load_dotenv
import jwt
from pydantic import BaseModel

from models import User, Plant

load_dotenv()

JWT_SECRET = getenv("JWT_SECRET")

router = APIRouter(prefix="/v1", tags=["user"])


class UserRegister(BaseModel):
    name: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


@router.post("/user/register")
async def create_user(u: UserRegister):
    """
    Create a user.
    """
    user = await User.find_one({"email": u.email})
    if user:
        raise HTTPException(status_code=409, detail="User already exists")
    
    hashed_password = bcrypt.hashpw(bytes(u.password, "utf-8"), bcrypt.gensalt())
    user = User(name=u.name, email=u.email, password=hashed_password, verification_code=int(''.join(random.choices(string.digits, k=5))))
    await user.commit()
    return await user.get_dict()


@router.post("/user/login")
async def login_user(u: UserLogin):
    """
    Login a user.
    """
    user = await User.find_one({"email": u.email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not bcrypt.checkpw(bytes(u.password, "utf-8"), bytes(user.password, "utf-8")):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"access_token": jwt.encode(await user.get_dict(), JWT_SECRET)}
    


@router.get("/user")
async def get_user(request: Request):
    """
    Retrieve a user by its ID.
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await user.get_dict()


@router.post("/user/verify")
async def verify_user(verification_code: int, request: Request):
    """
    Verify a user's email with a verification code.
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.verification_code != verification_code:
        raise HTTPException(status_code=400, detail="Invalid verification code")
    
    user.is_verified = True
    await user.commit()
    return await user.get_dict()


@router.put("/user/plant")
async def append_plant(plant_code: str, request: Request):
    """
    Append a plant to a user's list of plants.
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    plant = await Plant.find_one({"code": plant_code})
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    
    if user.plants is None:
        user.plants = []

    if plant in user.plants:
        raise HTTPException(status_code=409, detail="Plant already exists")
    
    user.plants.append(plant)
    await user.commit()

    return await user.get_dict()


@router.get("/user/plant")
async def get_user_plants(id: str, request: Request):
    """
    Retrieve a user's list of plants.
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    plants = [await Plant.find_one({"_id": plant.pk}) for plant in user.plants]
    return [await plant.get_dict() for plant in plants]
