"""
Module: Main Application
Author: Hirushiharan Thevendran
Organization: Lowcodeminds (Pvt) Ltd
Created On: 07/16/2024
Last Modified By: Hirushiharan
Last Modified On: 07/21/2024

Module Description: This module serves as the entry point for the FastAPI application. It runs the application using Uvicorn, the ASGI server.
The application is configured to listen on all network interfaces on port 8000.

Python Version: 3.11
"""

import uvicorn
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from src.api import app
from src.functions import settings
from src.utility_functions import log

def initialize_sentry():
    """
    Initialize Sentry for error tracking and performance monitoring.

    Configures Sentry with the DSN from settings and sets the traces sample rate.
    This function ensures that Sentry is properly set up to capture and report errors and performance issues.
    """
    try:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            traces_sample_rate=1.0,  # Adjust the sample rate as needed
        )
        log("Sentry initialized successfully.", level="INFO")
    except Exception as e:
        log(f"Error initializing Sentry: {e}", level="ERROR")
        raise

def main():
    """
    Main function to start the FastAPI application with Uvicorn server.

    Applies Sentry ASGI middleware to the FastAPI application and runs the Uvicorn server.
    The server listens on all network interfaces (0.0.0.0) on port 8000.
    """
    try:
        # Initialize Sentry for error tracking
        initialize_sentry()
        
        # Apply Sentry ASGI middleware to the FastAPI application
        app_with_sentry = SentryAsgiMiddleware(app)
        
        # Run the Uvicorn server
        uvicorn.run('src.api:app', host='0.0.0.0', port=8000)
    except Exception as e:
        log(f"Error running the application: {e}", level="ERROR")
        raise

if __name__ == '__main__':
    main()
