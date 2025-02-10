from fastapi import FastAPI, UploadFile, HTTPException, File
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from gridfs import GridFS
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os
from contextlib import asynccontextmanager
# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)


MONGODB_USERNAME = os.getenv("MONGODB_USERNAME")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
MONGODB_CLUSTER = os.getenv("MONGODB_CLUSTER", "metadata.oj7wh.mongodb.net")

uri = f"mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_CLUSTER}/?retryWrites=true&w=majority&appName=metadata"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["generate_hub"]
fs = GridFS(db)
collection = db["pdf_metadata"]


### Create FastAPI instance with custom docs and openapi url

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    try:
        client.admin.command('ping')
        print("Successfully connected to MongoDB!")
        yield
    except Exception as e:
        print(f"MongoDB connection error: {str(e)}")
        raise Exception("Failed to connect to database")
    finally:
        # Shutdown
        client.close()
        print("Closed MongoDB connection")
#might not be neccesary to passx in the urls
app = FastAPI(title="IllustrAI API",
    description="API for PDF processing and metadata management",
    docs_url="/api/py/docs",
    openapi_url="/api/py/openapi.json")

@app.get("/api/py/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

@app.post("/api/py/upload")
async def upload_pdf(file: UploadFile):
    """Uploads PDF to mongodb and returns file id"""
    try:
        contents = await file.read()
        file_id = fs.put(contents, filename=file.filename)
        return {"success": True, "file_id": str(file_id), "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await file.close()
    
@app.post("/api/py/process")
async def process_pdf(data: dict):
    """Processes PDF and returns metadata"""
    file_id = data.get("file_id")
    prompt = data.get("prompt")

    if not file_id or not prompt:
        raise HTTPException(status_code=400, detail="file_id and prompt are required")
        
    try:
        file_data = fs.get(ObjectId(file_id))
        pdf_content = file_data.read()

        #TODO: Process PDF content here
        print(f"Processing PDF content for file_id: {file_id}")
        
        return {"success": True, "message": "PDF content processed successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




