import firebase_admin
from firebase_admin import auth, credentials, firestore
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# Load Firebase credentials
cred = credentials.Certificate("firebase_config.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

class TokenModel(BaseModel):
    id_token: str  # The token received from Google Sign-In

@router.post("/login/")
def verify_google_token(token_data: TokenModel):
    try:
        decoded_token = auth.verify_id_token(token_data.id_token)
        uid = decoded_token["uid"]
        email = decoded_token.get("email", "No Email")

        # Store user in Firestore if not already added
        user_ref = db.collection("users").document(uid)
        user_data = user_ref.get()
        if not user_data.exists:
            user_ref.set({"email": email, "uid": uid})

        return {"message": "Login successful!", "uid": uid, "email": email}
    
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
