from fastapi import FastAPI
from auth import router as auth_router
from image_storage import router as storage_router
from wardrobe import router as wardrobe_router

app = FastAPI()

# Include routers for modular APIs
app.include_router(auth_router)
app.include_router(storage_router)
app.include_router(wardrobe_router)

@app.get("/")
def home():
    return {"message": "Welcome to VestiGo API!"}