from fastapi import FastAPI, Request, status, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import json
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
import mysql.connector
from mysql.connector import Error
from datetime import date, datetime

# Load environment variables from the .env file
load_dotenv()

class Settings(BaseSettings):
    MYSQL_ROOT_PASSWORD: str
    MYSQL_DATABASE: str
    MYSQL_USER: str = "root"
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306

    class Config:
        env_file = ".env"

settings = Settings()

# Database connection pooling
connection_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    pool_reset_session=True,
    host=settings.MYSQL_HOST,
    user=settings.MYSQL_USER,
    password=settings.MYSQL_ROOT_PASSWORD,
    database=settings.MYSQL_DATABASE,
    port=settings.MYSQL_PORT
)

app = FastAPI()
app.mount("/data", StaticFiles(directory="data"), name="data")

base_path = Path('data/')

# Dependency for database connection
def get_db_connection():
    try:
        connection = connection_pool.get_connection()
        if connection.is_connected():
            print("SQL Connection Successful")
            return connection
    except Error as err:
        print(f"Error: {err}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database connection error")

def format_response(data, request: Request, status_code: int) -> JSONResponse:
    """
    Helper function to format the response.
    """
    headers = dict(request.headers)
    content = {
        "success": status_code == status.HTTP_200_OK,
        "statusCode": status_code,
        "headers": headers,
        "totalCount": len(data) if status_code == status.HTTP_200_OK else 0,
        "data": data if status_code == status.HTTP_200_OK else None,
        "error": data if status_code != status.HTTP_200_OK else None
    }
    return JSONResponse(content=content, status_code=status_code)

def fetch_all_sql_table_data(table_name: str, db_conn) -> list:
    try:
        cursor = db_conn.cursor()
        query = "SELECT * FROM " + table_name
        cursor.execute(query)
        result = cursor.fetchall()
        
        # Convert date objects to strings
        columns = cursor.column_names
        data = []
        for row in result:
            row_data = {}
            for i, value in enumerate(row):
                if isinstance(value, (date, datetime)):
                    value = value.isoformat()
                row_data[columns[i]] = value
            data.append(row_data)
        
        return data
    except Error as err:
        print(f"Error: {err}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching data from database")
    finally:
        cursor.close()

@app.get("/")
async def root(request: Request):
    """
    Root endpoint to check if the app is running.
    """
    return format_response(data="Tower Management Azure app is running...", request=request, status_code=status.HTTP_200_OK)

@app.get("/closureData")
async def get_closure_data(request: Request, db_conn=Depends(get_db_connection)):
    """
    Endpoint to retrieve closure data from a Azure SQL table.
    """
    data = fetch_all_sql_table_data('tmsv_360_project_closure', db_conn)
    return format_response(data=data, request=request, status_code=status.HTTP_200_OK)

async def read_data_file(file_path: Path, request: Request) -> JSONResponse:
    """
    Utility function to read data from a JSON file.
    """
    try:
        if file_path.exists():
            with file_path.open('r') as file:
                data = json.load(file)
            print(f'Request for {file_path.name} received')
            return format_response(data=data, request=request, status_code=status.HTTP_200_OK)
        else:
            print(f'{file_path.name} file not found')
            return format_response(data="File not found", request=request, status_code=status.HTTP_404_NOT_FOUND)
    except json.JSONDecodeError:
        print("Error decoding JSON")
        return format_response(data="Malformed JSON", request=request, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
    except Exception as e:
        print(f"Error reading {file_path.name}: {e}")
        return format_response(data="Internal Server Error", request=request, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.get("/sunburstData")
async def get_sunburst_data(request: Request) -> JSONResponse:
    """
    Endpoint to retrieve sunburst chart data from a JSON file.
    """
    file_path = base_path + 'sunburstData.json'
    return await read_data_file(file_path, request)

@app.get("/gridData")
async def get_grid_data(request: Request) -> JSONResponse:
    """
    Endpoint to retrieve grid data from a JSON file.
    """
    file_path = base_path + 'gridData.json'
    return await read_data_file(file_path, request)

@app.exception_handler(400)
async def bad_request_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler for 400 Bad Request
    """
    return format_response(data="Bad Request", request=request, status_code=status.HTTP_400_BAD_REQUEST)

@app.exception_handler(408)
async def request_timeout_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler for 408 Request Timeout
    """
    return format_response(data="Request Timeout", request=request, status_code=status.HTTP_408_REQUEST_TIMEOUT)

@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler for 500 Internal Server Error
    """
    return format_response(data="Internal Server Error", request=request, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000)
