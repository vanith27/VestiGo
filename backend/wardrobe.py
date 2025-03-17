import firebase_admin
from firebase_admin import firestore
from fastapi import APIRouter, HTTPException

router = APIRouter()

# Firebase Firestore reference
db = firestore.client()

@router.post("/add-item/")
def add_item(name: str, category: str):
    try:
        doc_ref = db.collection("wardrobe").document()
        doc_ref.set({"name": name, "category": category})

        return {"message": f"Item '{name}' added to wardrobe!"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding item: {str(e)}")

@router.get("/get-items/")
def get_items():
    try:
        items = []
        docs = db.collection("wardrobe").stream()
        for doc in docs:
            item = doc.to_dict()
            item["id"] = doc.id  # Include Firestore document ID
            items.append(item)

        return {"wardrobe": items}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching items: {str(e)}")