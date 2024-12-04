import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import jwt
from motor.motor_asyncio import AsyncIOMotorClient

from models import instance, User
from routers import ALL

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
JWT_SECRET = os.getenv("JWT_SECRET")


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
    

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
	request.state.user = None
	authorization = request.headers.get("Authorization")
	if authorization:
		try:
			token = authorization.split(" ")[1]
			payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
			request.state.user = await User.find_one({"email": payload["email"]})
		except jwt.PyJWTError:
			pass
		except IndexError:
			pass
		except Exception as e:
			print(e)
	response = await call_next(request)
	return response


@app.get("/", include_in_schema=False)
def root():
    return {"message": "I think, you're not supposed to be here."}

