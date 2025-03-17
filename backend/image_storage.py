import boto3
import uuid
from fastapi import APIRouter, File, UploadFile
from dotenv import load_dotenv
import os
from botocore.config import Config  # Import for signature version enforcement

# Load environment variables
load_dotenv()

router = APIRouter()

# AWS S3 Configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-2")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# Debug: Print environment variables
print(f"DEBUG: AWS_REGION = {AWS_REGION}")
print(f"DEBUG: S3_BUCKET_NAME = {S3_BUCKET_NAME}")

# Function to initialize S3 client
def get_s3_client():
    session = boto3.session.Session()
    return session.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
        config=Config(signature_version="s3v4") 
)

# Initialize S3 client
s3_client = get_s3_client()

# Upload Image (Stored Privately)
@router.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    try:
        # Generate a unique filename
        file_ext = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_ext}"

         # Debug: Print upload details
        print(f"DEBUG: Uploading {unique_filename} to bucket {S3_BUCKET_NAME}")

        # Upload to S3 (Private by default)
        s3_client.upload_fileobj(
            file.file,
            S3_BUCKET_NAME,
            unique_filename,
            ExtraArgs={"ContentType": file.content_type}
        )

        print(f"DEBUG: Upload successful! File: {unique_filename}")

        return {"message": "Upload successful!", "file_name": unique_filename, "bucket_name":S3_BUCKET_NAME, "AWS Region": AWS_REGION}

    except Exception as e:
        return {"error": str(e)}

### **✅ Generate Signed URL for Secure Access**
@router.get("/generate-signed-url/")
def generate_presigned_url(file_name: str):
    """
    Generates a signed URL to securely access an image stored in AWS S3.
    The URL will expire after 1 hour (3600 seconds).
    """
    print(f"DEBUG: Generating signed URL for {file_name} in bucket {S3_BUCKET_NAME}")
    try:
        # Debug: Print retrieval details
        
        signed_url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": S3_BUCKET_NAME, "Key": file_name },
            #Params={"Bucket": "vestigo-app-images", "Key": file_name, "signingRegion": AWS_REGION},
            ExpiresIn=3600  # URL valid for 1 hour
        )
        print(f"DEBUG: Signed URL generated: {signed_url}")
        return {"signed_url": signed_url}
    
    except Exception as e:
        print(f"ERROR: Failed to generate signed URL - {str(e)}")
        return {"error": str(e)}

