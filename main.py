from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import json
from pathlib import Path

app = FastAPI()
app.mount("/data", StaticFiles(directory="data"), name="data")

@app.get("/")
async def root():
    """
    Root endpoint to check if the app is running.
    """
    return {"message": "Tower Management Azure app is running..."}

@app.get("/sunburstData", response_class=JSONResponse)
async def get_sunburst_data(request: Request):
    """
    Endpoint to retrieve sunburst chart data from a JSON file.

    :param request: FastAPI Request object
    :return: JSON response with sunburst chart data or an error message
    """
    file_path = Path('data/sunburstData.json')
    try:
        if file_path.exists():
            with file_path.open('r') as file:
                data = json.load(file)
            print('Request for Sunburst Chart Data received')
            return JSONResponse(content=data)
        else:
            print('Sunburst Chart Data file not found')
            return JSONResponse(content={"error": "File not found"}, status_code=404)
    except Exception as e:
        print(f"Error reading Sunburst Chart Data: {e}")
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)

@app.get("/gridData", response_class=JSONResponse)
async def get_grid_data(request: Request):
    """
    Endpoint to retrieve grid data from a JSON file.

    :param request: FastAPI Request object
    :return: JSON response with grid data or an error message
    """
    file_path = Path('data/gridData.json')
    try:
        if file_path.exists():
            with file_path.open('r') as file:
                data = json.load(file)
            print('Request for Grid Data received')
            return JSONResponse(content=data)
        else:
            print('Grid Data file not found')
            return JSONResponse(content={"error": "File not found"}, status_code=404)
    except Exception as e:
        print(f"Error reading Grid Data: {e}")
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000)
