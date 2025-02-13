from fastapi import FastAPI, UploadFile, HTTPException
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from gridfs import GridFS
from bson.objectid import ObjectId
from dotenv import load_dotenv
from api.processor import PDFProcessingService
import os
from contextlib import asynccontextmanager
import uvicorn
from starlette.middleware.cors import CORSMiddleware

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)


MONGODB_USERNAME = os.getenv("MONGODB_USERNAME")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
MONGODB_CLUSTER = os.getenv("MONGODB_CLUSTER", "metadata.oj7wh.mongodb.net")


uri = f"mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_CLUSTER}/?retryWrites=true&w=majority&appName=metadata&tls=true"
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
    openapi_url="/api/py/openapi.json",  lifespan=lifespan, root_path_in_servers=False,
    timeout=600    )
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(
        "api.index:app",
        host="0.0.0.0",
        port=8000,
        timeout_keep_alive=600,
        limit_concurrency=10,
        limit_max_requests=10,
        workers=4 , # Adjust based on your CPU cores
          timeout_graceful_shutdown=300 
    )

@app.get("/api/py/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

@app.post("/api/py/upload")
async def upload_pdf(file: UploadFile):
    """Uploads PDF to mongodb and returns file id"""
    try:
        print(f"Uploading file: {file.filename}")
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
    print("processing pdf...")
    file_id = data.get("file_id")
    prompt = data.get("prompt")

    if not file_id or not prompt:
        raise HTTPException(status_code=400, detail="file_id and prompt are required")
        
    try:
        file_data = fs.get(ObjectId(file_id))
        pdf_content = file_data.read()

        processing_service = PDFProcessingService()
        result = await processing_service.process_document(pdf_content, prompt)
       
        return {"success": True, "results": result["results"]}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




