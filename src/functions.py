"""
Module: Functions
Author: Hirushiharan Thevendran
Organization: Lowcodeminds (Pvt) Ltd
Created On: 07/16/2024
Last Modified By: Hirushiharan
Last Modified On: 07/19/2024

Module Description: This module contains utility functions for the FastAPI application, including logging, database connection pooling,
data fetching, and file reading. The functions are designed to interact with a MySQL database and handle JSON data files.

Functions:
    - log: Logs messages with a timestamp and log level.
    - create_connection_pool: Creates a MySQL connection pool with a retry mechanism.
    - get_db_connection: Retrieves a MySQL database connection from the pool with a retry mechanism.
    - fetch_all_sql_table_data: Fetches all data from a specified SQL table, converting date fields to ISO format.
    - read_data_file: Reads data from a JSON file and returns a JSONResponse with appropriate error handling.
    
Python Version: 3.11
"""

import json
import time
from datetime import date, datetime
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
import mysql.connector
from mysql.connector import Error
from fastapi import Request, status, HTTPException
from fastapi.responses import JSONResponse
from mysql.connector.pooling import MySQLConnectionPool
from pathlib import Path
from starlette.middleware.base import BaseHTTPMiddleware

INFO = "INFO"
WARNING = "WARNING"
ERROR = "ERROR"
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 MB
LOG_FILE = "logs/application.log"

def rotate_log_file():
    """
    Rotates the log file when its size exceeds the maximum allowed size.

    This function checks if the current log file exceeds the predefined maximum
    size (5 MB). If it does, the function renames the current log file to include
    a timestamp in its name and retains it as an old log file. The timestamp
    format used is 'YYYYMMDD_HHMMSS' to ensure uniqueness and chronological
    sorting of old log files.

    The log file is renamed with the format: 'YYYYMMDD_HHMMSS-application.log'.

    Returns:
        None
    """
    if Path(LOG_FILE).exists() and Path(LOG_FILE).stat().st_size > MAX_LOG_SIZE:
        # Generate a timestamp for the old log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_log_file_name = f"{timestamp}-{LOG_FILE}"
        
        # Rotate the log file
        Path(LOG_FILE).rename(new_log_file_name)

def log(message: str, level: str = INFO) -> None:
    """
    Log messages with a timestamp and a specific log level.
    Supports logging to both the console and a file in JSON format.

    Args:
        message (str): The message to log.
        level (str): The log level (e.g., INFO, WARNING, ERROR).
    
    Returns:
        None
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = {
        "timestamp": timestamp,
        "level": level,
        "message": message
    }
    log_message_str = json.dumps(log_message)
    
    print(f"{timestamp} [{level}] {message}")
    
    # Write to log file
    with open(LOG_FILE, "a") as log_file:
        log_file.write(log_message_str + "\n")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Log request details
        log_message = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers)
        }
        log(message=json.dumps(log_message), level="INFO")
        
        response = await call_next(request)
        
        # Log response details
        log_message = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status_code": response.status_code
        }
        log(message=json.dumps(log_message), level="INFO")
        
        return response
    
# DEPRECATED FUNTION
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

def create_connection_pool() -> MySQLConnectionPool:
    """
    Create a MySQL connection pool with retry mechanism.

    Returns:
        MySQLConnectionPool: A pool of MySQL connections.
    
    Raises:
        HTTPException: If there's an error creating the connection pool.
    """
    retries = 3
    for attempt in range(retries):
        try:
            log("Creating connection pool...", "INFO")
            return MySQLConnectionPool(
                pool_name="TMSV_Pool",
                pool_size=10,
                pool_reset_session=True,
                host=settings.MYSQL_HOST,
                user=settings.MYSQL_USER,
                password=settings.MYSQL_ROOT_PASSWORD,
                database=settings.MYSQL_DATABASE,
                port=settings.MYSQL_PORT,
                connection_timeout=300
            )
        except Error as err:
            log(f"Attempt {attempt + 1}: Error creating connection pool: {err}", "ERROR")
            if attempt + 1 == retries:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database connection pool creation error")
            time.sleep(2)

connection_pool = create_connection_pool()

def get_db_connection() -> mysql.connector.MySQLConnection:
    """
    Get a database connection from the connection pool with retry mechanism.

    Returns:
        MySQLConnection: A MySQL database connection.
    
    Raises:
        HTTPException: If unable to get a connection after retries.
    """
    retries = 3
    for attempt in range(retries):
        try:
            connection = connection_pool.get_connection()
            if connection.is_connected():
                log("SQL Connection Successful", "INFO")
                return connection
        except Error as err:
            log(f"Attempt {attempt + 1}: Error getting connection: {err}", "ERROR")
            if attempt + 1 == retries:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database connection error")
            time.sleep(2)

def fetch_all_sql_table_data(table_name: str, db_conn) -> list:
    """
    Fetch all data from the specified SQL table.

    Args:
        table_name (str): The name of the SQL table.
        db_conn (MySQLConnection): The database connection.

    Returns:
        list: A list of rows from the table, with date fields converted to ISO format.

    Raises:
        HTTPException: If there's an error fetching data from the database.
    """
    try:
        cursor = db_conn.cursor()
        query = f"SELECT * FROM {table_name}"
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
        
        log(f"Fetched data from table '{table_name}'", "INFO")
        return data
    except Error as err:
        log(f"Error fetching data from table '{table_name}': {err}", "ERROR")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching data from database")
    finally:
        cursor.close()

async def read_data_file(file_path: Path, request: Request) -> JSONResponse:
    """
    Utility function to read data from a JSON file.

    Args:
        file_path (Path): The path to the JSON file.
        request (Request): The HTTP request object.

    Returns:
        JSONResponse: A JSON response with the file content or an error message.
    """
    try:
        if file_path.exists():
            with file_path.open('r') as file:
                data = json.load(file)
            log(f"Request for {file_path.name} received", "INFO")
            return JSONResponse(content=data, status_code=status.HTTP_200_OK)
        else:
            log(f"{file_path.name} file not found", "ERROR")
            return JSONResponse(content="File not found", status_code=status.HTTP_404_NOT_FOUND)
    except json.JSONDecodeError:
        log("Error decoding JSON", "ERROR")
        return JSONResponse(content="Malformed JSON", status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
    except Exception as e:
        log(f"Error reading {file_path.name}: {e}", "ERROR")
        return JSONResponse(content="Internal Server Error", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
