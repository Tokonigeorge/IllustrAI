from fastapi import FastAPI, UploadFile, File, HTTPException
import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from gridfs import GridFS
from bson.objectid import ObjectId
# from fastapi.responses import JSONResponse

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)
MONGODB_USERNAME = os.getenv("MONGODB_USERNAME")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
MONGODB_CLUSTER = os.getenv("MONGODB_CLUSTER", "metadata.oj7wh.mongodb.net")

### Create FastAPI instance with custom docs and openapi url
#might not be neccesary to passx in the urls
app = FastAPI(docs_url="/api/py/docs", openapi_url="/api/py/openapi.json")



MONGODB_USERNAME = os.getenv("MONGODB_USERNAME")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
MONGODB_CLUSTER = os.getenv("MONGODB_CLUSTER", "metadata.oj7wh.mongodb.net")
uri = f"mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_CLUSTER}/?retryWrites=true&w=majority&appName=metadata"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
    raise HTTPException(status_code=500, detail=str(e))

    


db = client["generate_hub"]
fs = GridFS(db)
collection = db["pdf_metadata"]

@app.get("/api/py/helloFastApi")
async def root():

    """Health check endpoint"""
    return {"status": "ok"}

@app.post("/api/py/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Uploads PDF to mongodb and returns file id"""
    try:
        file_id = fs.put(file.file, filename=file.filename)
        return {"success": True, "file_id": str(file_id), "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
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




