from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.dependencies import get_s3_client
from dotenv import load_dotenv

from app.utils import clean_images_response

load_dotenv('.env')
app = FastAPI()

# CORS (Cross-Origin Resource Sharing) middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get the S3 client
s3 = Depends(get_s3_client)

# AWS S3 bucket name
BUCKET_NAME = "portfolio-asset-data"

# Endpoint to upload an image to S3
@app.post("/upload")
async def upload_file(file: UploadFile = File(...), s3: s3 = Depends(get_s3_client)):
    try:
        # Upload file to S3
        s3.upload_fileobj(file.file, BUCKET_NAME, file.filename)
        return {"message": "File uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Endpoint to get the URL of an image from S3
@app.get("/get_image_url/{image_key}")
async def get_image_url(image_key: str, s3: s3 = Depends(get_s3_client)):
    try:
        # Generate a presigned URL for the image, expects images/<key>
        url = s3.generate_presigned_url("get_object", Params={"Bucket": BUCKET_NAME, "Key": f"images/{image_key}"})
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Get all images
@app.get("/images")
async def get_images(s3: s3 = Depends(get_s3_client)):
    try:
        # List all objects in the S3 bucket
        response = s3.list_objects_v2(Bucket=BUCKET_NAME)
        
        # Extract URLs or other relevant information
        images_info = [
            {
                "url": s3.generate_presigned_url(
                    "get_object", Params={"Bucket": BUCKET_NAME, "Key": obj["Key"]}
                ),
                "key": obj["Key"],
            }
            for obj in response.get("Contents", [])
        ]
        result = clean_images_response(images_info)
        
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))