"""
Module: API
Author: Hirushiharan Thevendran
Organization: Lowcodeminds (Pvt) Ltd
Created On: 07/16/2024
Last Modified By: Hirushiharan
Last Modified On: 07/19/2024

Module Description: This module defines the FastAPI application and its endpoints. The endpoints interact with the database and
serve JSON responses for different types of data, including closure data and JSON files. The module also includes custom exception
handlers for various HTTP errors.

Endpoints:
    - root: Checks if the app is running.
    - get_closure_data: Retrieves closure data from an SQL table.
    - get_sunburst_data: Retrieves sunburst chart data from a JSON file.
    - get_grid_data: Retrieves grid data from a JSON file.
    - bad_request_handler: Handles 400 Bad Request errors.
    - request_timeout_handler: Handles 408 Request Timeout errors.
    - internal_server_error_handler: Handles 500 Internal Server Error errors.

Python Version: 3.11
"""

from fastapi import FastAPI, Request, Depends, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pathlib import Path
from . import functions as fn

description = """
Tower Management System API provides endpoints to interact with the Tower Management SQL database and access JSON files. 

## Endpoints

### Root

- **GET /**: Check if the application is running.

### Closure Data

- **GET /closureData**: Retrieve closure data from the SQL database.

### Sunburst Data

- **GET /sunburstData**: Retrieve sunburst chart data from a JSON file.

### Grid Data

- **GET /gridData**: Retrieve grid data from a JSON file.

## Features

- **Read Closure Data**: Fetch detailed information on project closures.
- **Read Sunburst Data**: Access data used for visualizing hierarchical relationships.
- **Read Grid Data**: Obtain grid-related data for visual representation or analysis.

For detailed information and usage examples, refer to the API documentation on the provided endpoints.
"""

app = FastAPI(
    title="Tower Management System APIs",
    description=description,
    version="1.0.0",
    contact={
        "name": "Hirushiharan Thevendran",
        "email": "hirushiharant@gmail.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)
app.add_middleware(fn.LoggingMiddleware)
app.mount("/data", StaticFiles(directory="data"), name="data")

base_path = Path('data/')

@app.get("/")
async def root(request: Request):
    """
    Root endpoint to check if the app is running.
    """
    return JSONResponse(content="Tower Management Azure app is running...", status_code=status.HTTP_200_OK)

@app.get("/closureData")
async def get_closure_data(request: Request, db_conn=Depends(fn.get_db_connection)):
    """
    Endpoint to retrieve closure data from an Azure SQL table.

    Args:
        request (Request): The HTTP request object.
        db_conn (MySQLConnection): The database connection.

    Returns:
        JSONResponse: A JSON response with the closure data.
    """
    data = fn.fetch_all_sql_table_data('tmsv_360_project_closure', db_conn)
    return JSONResponse(content=data, status_code=status.HTTP_200_OK)

@app.get("/sunburstData")
async def get_sunburst_data(request: Request) -> JSONResponse:
    """
    Endpoint to retrieve sunburst chart data from a JSON file.

    Args:
        request (Request): The HTTP request object.

    Returns:
        JSONResponse: A JSON response with the sunburst chart data.
    """
    file_path = base_path / 'sunburstData.json'
    return await fn.read_data_file(file_path, request)

@app.get("/gridData")
async def get_grid_data(request: Request) -> JSONResponse:
    """
    Endpoint to retrieve grid data from a JSON file.

    Args:
        request (Request): The HTTP request object.

    Returns:
        JSONResponse: A JSON response with the grid data.
    """
    file_path = base_path / 'gridData.json'
    return await fn.read_data_file(file_path, request)

@app.exception_handler(400)
async def bad_request_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler for 400 Bad Request

    Args:
        request (Request): The HTTP request object.
        exc (Exception): The exception that occurred.

    Returns:
        JSONResponse: A JSON response with the error message.
    """
    return JSONResponse(content="Bad Request", status_code=status.HTTP_400_BAD_REQUEST)

@app.exception_handler(408)
async def request_timeout_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler for 408 Request Timeout

    Args:
        request (Request): The HTTP request object.
        exc (Exception): The exception that occurred.

    Returns:
        JSONResponse: A JSON response with the error message.
    """
    return JSONResponse(content="Request Timeout", status_code=status.HTTP_408_REQUEST_TIMEOUT)

@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler for 500 Internal Server Error

    Args:
        request (Request): The HTTP request object.
        exc (Exception): The exception that occurred.

    Returns:
        JSONResponse: A JSON response with the error message.
    """
    return JSONResponse(content="Internal Server Error", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DatabaseConnectionError(Exception):
    pass

class DataFetchError(Exception):
    pass

@app.exception_handler(DatabaseConnectionError)
async def database_connection_error_handler(request: Request, exc: DatabaseConnectionError) -> JSONResponse:
    return JSONResponse(content="Database connection error", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)