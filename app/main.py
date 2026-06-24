from fastapi import FastAPI
from app.database import engine,Base
import app.models
from app.routes import users

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(users.router)

@app.get("/")
def Home():
    return {"message":"Home api running successfully"}


