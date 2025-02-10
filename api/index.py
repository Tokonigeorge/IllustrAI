from fastapi import FastAPI, FormField
from fastapi.responses import JSONResponse
from pymongo import MongoClient

### Create FastAPI instance with custom docs and openapi url
#might not be neccesary to pass in the urls
app = FastAPI(docs_url="/api/py/docs", openapi_url="/api/py/openapi.json")

#Connect to MongoDB;
client = MongoClient("mongodb://localhost:27017/")

@app.get("/api/py/helloFastApi")
def hello_fast_api():
    return {"message": "Hello from FastAPI"}