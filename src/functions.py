"""
Module: Functions
Author: Hirushiharan Thevendran
Organization: Lowcodeminds (Pvt) Ltd
Created On: 07/16/2024
Last Modified By: Hirushiharan
Last Modified On: 07/21/2024

Module Description: This module contains utility functions for the FastAPI application, including logging, database connection pooling,
data fetching, and file reading. The functions are designed to interact with a MySQL database and handle JSON data files.

Functions:
    - LoggingMiddleware: Middleware for logging request and response details.
    - Settings: Configuration class to load settings from environment variables.
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
from pydantic_settings import BaseSettings
import mysql.connector
from mysql.connector import Error
from fastapi import Request, status, HTTPException
from fastapi.responses import JSONResponse
from mysql.connector.pooling import MySQLConnectionPool
from starlette.middleware.base import BaseHTTPMiddleware
from . import utility_functions as ufn

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging request and response details.

    This middleware logs details about incoming HTTP requests and outgoing responses.
    Logs include timestamp, request method, URL, headers, and response status code.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Log request details
        log_message = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers)
        }
        ufn.log(message=json.dumps(log_message), level="INFO")
        
        response = await call_next(request)
        
        # Log response details
        log_message = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status_code": response.status_code
        }
        ufn.log(message=json.dumps(log_message), level="INFO")
        
        return response

class Settings(BaseSettings):
    """
    Configuration class to load settings from environment variables.

    Attributes:
        MYSQL_PASSWORD (str): The root password for MySQL.
        MYSQL_DATABASE (str): The name of the MySQL database.
        MYSQL_USER (str): The MySQL user.
        MYSQL_HOST (str): The MySQL host.
        MYSQL_PORT (int): The port for MySQL connection.
        SENTRY_DSN (str): The Sentry DSN for error tracking.
    """
    
    MYSQL_PASSWORD: str
    MYSQL_DATABASE: str
    MYSQL_USER: str
    MYSQL_HOST: str
    SENTRY_DSN: str
    MYSQL_PORT: int

    class Config:
        """
        Configuration for Pydantic settings.
        
        Specifies the environment file from which to load settings.
        """
        env_file = ".env"

settings = Settings()

def create_connection_pool() -> MySQLConnectionPool:
    """
    Create a MySQL connection pool with a retry mechanism.

    Tries to create a MySQL connection pool with retry logic. Logs attempts and errors.
    
    Returns:
        MySQLConnectionPool: A pool of MySQL connections.

    Raises:
        HTTPException: If there's an error creating the connection pool after retries.
    """
    retries = 3
    for attempt in range(retries):
        try:
            ufn.log("Creating connection pool...", "INFO")
            return MySQLConnectionPool(
                pool_name="TMSV_Pool",
                pool_size=10,
                pool_reset_session=True,
                host=settings.MYSQL_HOST,
                user=settings.MYSQL_USER,
                password=settings.MYSQL_PASSWORD,
                database=settings.MYSQL_DATABASE,
                port=settings.MYSQL_PORT,
                connection_timeout=300
            )
        except Error as err:
            ufn.log(f"Attempt {attempt + 1}: Error creating connection pool: {err}", "ERROR")
            if attempt + 1 == retries:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database connection pool creation error")
            time.sleep(2)

connection_pool = create_connection_pool()

def get_db_connection() -> mysql.connector.MySQLConnection:
    """
    Retrieve a MySQL database connection from the pool with retry mechanism.

    Attempts to get a connection from the pool with retry logic. Logs success and errors.
    
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
                ufn.log("SQL Connection Successful", "INFO")
                return connection
        except Error as err:
            ufn.log(f"Attempt {attempt + 1}: Error getting connection: {err}", "ERROR")
            if attempt + 1 == retries:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database connection error")
            time.sleep(2)

def fetch_all_sql_table_data(table_name: str, db_conn) -> list:
    """
    Fetch all data from a specified SQL table.

    Executes a query to fetch all data from the given table. Converts date fields to ISO format.
    
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
        
        ufn.log(f"Fetched data from table '{table_name}'", "INFO")
        return data
    except Error as err:
        ufn.log(f"Error fetching data from table '{table_name}': {err}", "ERROR")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching data from database")
    finally:
        cursor.close()

async def read_data_file(file_path: Path, request: Request) -> JSONResponse:
    """
    Utility function to read data from a JSON file.

    Reads the JSON file at the specified path and returns a JSONResponse with the file content.
    Logs the request and any errors encountered.
    
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
            ufn.log(f"Request for {file_path.name} received", "INFO")
            return JSONResponse(content=data, status_code=status.HTTP_200_OK)
        else:
            ufn.log(f"{file_path.name} file not found", "ERROR")
            return JSONResponse(content="File not found", status_code=status.HTTP_404_NOT_FOUND)
    except json.JSONDecodeError:
        ufn.log("Error decoding JSON", "ERROR")
        return JSONResponse(content="Malformed JSON", status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
    except Exception as e:
        ufn.log(f"Error reading {file_path.name}: {e}", "ERROR")
        return JSONResponse(content="Internal Server Error", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
