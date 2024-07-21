"""
Module: Utility Functions
Author: Hirushiharan Thevendran
Organization: Lowcodeminds (Pvt) Ltd
Created On: 07/16/2024
Last Modified By: Hirushiharan
Last Modified On: 07/21/2024

Module Description: This module contains utility functions for the FastAPI application, including logging, database connection pooling,
data fetching, and file reading. The functions are designed to interact with a MySQL database and handle JSON data files.

Functions:
    - log: Logs messages with a timestamp and log level.
    - create_log_file: Ensures the log file exists.
    - rotate_log_file: Rotates the log file when it exceeds a specified size.
    - format_response: Formats responses for the FastAPI application.
    
Python Version: 3.11
"""

import json
from datetime import datetime
from pathlib import Path
from fastapi import Request, status
from fastapi.responses import JSONResponse

# Constants for log levels and log file management
INFO = "INFO"
WARNING = "WARNING"
ERROR = "ERROR"
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 MB
LOG_FILE = "logs/application.log"

def create_log_file():
    """
    Ensures the log file exists.

    This function checks if the log file specified by LOG_FILE exists. 
    If it does not, the function creates an empty log file.
    
    Returns:
        None
    """
    if not Path(LOG_FILE).exists():
        Path(LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "x") as file:
            file.close()

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
    Logs messages with a timestamp and a specific log level.
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
    
    # Print log message to the console
    print(f"{timestamp} [{level}] {message}")
    
    # Rotate log file if necessary
    rotate_log_file()
    create_log_file()

    # Write log message to the log file
    with open(LOG_FILE, "a") as log_file:
        log_file.write(log_message_str + "\n")

def format_response(data, request: Request, status_code: int) -> JSONResponse:
    """
    Helper function to format the response for the FastAPI application.

    Args:
        data: The data to include in the response.
        request (Request): The FastAPI request object.
        status_code (int): The HTTP status code for the response.

    Returns:
        JSONResponse: The formatted JSON response.
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
