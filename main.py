from fastapi import FastAPI, Form, Request, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import json
from pathlib import Path

app = FastAPI()
app.mount("/data", StaticFiles(directory="data"), name="data")

# To check if the app is running
@app.get("/")
async def root():
    return {"message": "Hello, World!"}

@app.get("/sunburstData", response_class=JSONResponse)
async def index(request: Request):
    # Reading the JSON file
    file_path = Path('data/sunburstData.json')
    if file_path.exists():
        with file_path.open('r') as file:
            data = json.load(file)
        print('Request for Sunburst Chart Data received')
        return JSONResponse(content=data)
    else:
        return JSONResponse(content={"error": "File not found"}, status_code=404)

@app.get("/gridData", response_class=JSONResponse)
async def index(request: Request):
    # Reading the JSON file
    file_path = Path('data/gridData.json')
    if file_path.exists():
        with file_path.open('r') as file:
            data = json.load(file)
        print('Request for Sunburst Chart Data received')
        return JSONResponse(content=data)
    else:
        return JSONResponse(content={"error": "File not found"}, status_code=404)
    
if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000)