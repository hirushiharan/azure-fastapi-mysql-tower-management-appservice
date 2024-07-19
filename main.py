"""
Module: Main Application
Author: Hirushiharan Thevendran
Organization: Lowcodeminds (Pvt) Ltd
Created On: 07/16/2024
Last Modified By: Hirushiharan
Last Modified On: 07/19/2024

Module Description: This module serves as the entry point for the FastAPI application. It runs the application using Uvicorn, the ASGI server.
The application is configured to listen on all network interfaces on port 8000.

Python Version: 3.11
"""

import uvicorn

if __name__ == '__main__':
    uvicorn.run('src.api:app', host='0.0.0.0', port=8000)
