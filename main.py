import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

from models import instance
from routers import ALL

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

client = AsyncIOMotorClient(MONGO_URI)
db = client["data"]
instance.set_db(db)

app = FastAPI(title="Plant Console API", version="0.1.0")
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

for router in ALL:
    app.include_router(router)

@app.get("/", include_in_schema=False)
def root():
    return {"message": "I think, you're not supposed to be here."}

