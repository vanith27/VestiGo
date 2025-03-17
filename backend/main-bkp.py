import firebase_admin
from firebase_admin import credentials, firestore, auth
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

# Initialize FastAPI
app = FastAPI()

# Load Firebase credentials
cred = credentials.Certificate("firebase_config.json")
firebase_admin.initialize_app(cred)

# Connect to Firestore
db = firestore.client()

class TokenModel(BaseModel):
    id_token: str  # The token received from Google Sign-In

# API to verify Google Sign-In token
@app.post("/login/")
def verify_google_token(token_data: TokenModel):
    try:
        # Verify the ID token with Firebase Auth
        decoded_token = auth.verify_id_token(token_data.id_token)
        uid = decoded_token["uid"]
        email = decoded_token.get("email", "No Email")

        # Check if user exists in Firestore, if not, create a new user
        user_ref = db.collection("users").document(uid)
        user_data = user_ref.get()

        if not user_data.exists:
            user_ref.set({"email": email, "uid": uid})

        return {"message": "Login successful!", "uid": uid, "email": email}

    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
        
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