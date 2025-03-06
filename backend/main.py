import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import FastAPI

# Initialize FastAPI
app = FastAPI()

# Load Firebase credentials
cred = credentials.Certificate("firebase_config.json")
firebase_admin.initialize_app(cred)

# Connect to Firestore
db = firestore.client()

@app.get("/")
def home():
    return {"message": "Welcome to VestiGo API!"}

# New API to add an item
@app.post("/add-item/")
def add_item(name: str, category: str):
    doc_ref = db.collection("wardrobe").document()
    doc_ref.set({
        "name": name,
        "category": category
    })
    return {"message": f"Item {name} added to wardrobe!"}

# API to retrieve all wardrobe items
@app.get("/get-items/")
def get_items():
    items = []
    docs = db.collection("wardrobe").stream()
    for doc in docs:
        item = doc.to_dict()
        item["id"] = doc.id  # Add Firestore document ID
        items.append(item)
    return {"wardrobe": items}