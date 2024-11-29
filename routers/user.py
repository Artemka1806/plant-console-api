import random
import string

from bson import ObjectId
from fastapi import APIRouter
from fastapi import HTTPException

from models import User, Plant

router = APIRouter(prefix="/v1", tags=["user"])


@router.post("/user")
async def create_user(name: str, email: str):
    """
    Create a user.
    """
    user = await User.find_one({"email": email})
    if user:
        raise HTTPException(status_code=409, detail="User already exists")
    
    user = User(name=name, email=email, verification_code=int(''.join(random.choices(string.digits, k=5))))
    await user.commit()
    return await user.get_dict()


@router.get("/user/{id}")
async def get_user(id: str):
    """
    Retrieve a user by its ID.
    """
    user = await User.find_one({"_id": ObjectId(id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await user.get_dict()


@router.post("/user/{id}/verify")
async def verify_user(id: str, verification_code: int):
    """
    Verify a user's email with a verification code.
    """
    user = await User.find_one({"_id": ObjectId(id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.verification_code != verification_code:
        raise HTTPException(status_code=400, detail="Invalid verification code")
    
    user.is_verified = True
    await user.commit()
    return await user.get_dict()


@router.put("/user/{id}/plant")
async def append_plant(id: str, plant_code: str):
    """
    Append a plant to a user's list of plants.
    """
    user = await User.find_one({"_id": ObjectId(id)})
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


@router.get("/user/{id}/plants")
async def get_user_plants(id: str):
    """
    Retrieve a user's list of plants.
    """
    user = await User.find_one({"_id": ObjectId(id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    plants = [await Plant.find_one({"_id": plant.pk}) for plant in user.plants]
    return [await plant.get_dict() for plant in plants]
