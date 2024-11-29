import datetime
import random
import string

from bson import ObjectId
from fastapi import APIRouter
from fastapi import HTTPException

from models import Plant

router = APIRouter(prefix="/v1", tags=["plant"])


@router.post("/plant")
async def create_plant():
    """
    Create a plant.
    """
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        if not await Plant.find_one({"code": code}):
            plant = Plant(code=code)
            await plant.commit()
            return await plant.get_dict()


@router.get("/plant/{id}")
async def get_plant(id: str):
    """
    Retrieve a plant by its ID.
    """
    plant = await Plant.find_one({"_id": ObjectId(id)})
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    return await plant.get_dict()


@router.put("/plant/{id}")
async def update_plant(id: str, name: str = None, points: int = None, level: int = None, money: int = None, last_watered_at: int = None):
    """
    Update a plant by its ID.
    """
    if not await Plant.find_one({"_id": ObjectId(id)}):
        raise HTTPException(status_code=404, detail="Plant not found")
    
    plant = await Plant.find_one({"_id": ObjectId(id)})
    plant.name = name
    plant.points = points
    plant.level = level
    plant.money = money
    plant.last_watered_at = datetime.datetime.utcfromtimestamp(last_watered_at)
    await plant.commit()

    return await plant.get_dict()