from .plant import router as plant_router
from .user import router as user_router

ALL = [
    plant_router,
    user_router
]