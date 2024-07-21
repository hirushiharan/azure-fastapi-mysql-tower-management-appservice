# Azure FastAPI MySQL Tower Management AppService

This FastAPI application serves as a backend for managing and retrieving data for an LCM Tower Management system application. It provides endpoints to check if the app is running, fetch data for Sunburst and Grid charts from JSON files, and fetch Closure data from a MySQL database.

## Endpoints

- **GET /**: Returns a message indicating that the Tower Management Azure app is running.
- **GET /sunburstData**: Returns the data for the Sunburst chart from a JSON file.
- **GET /gridData**: Returns the data for the Grid chart from a JSON file.
- **GET /closureData**: Returns the data for the Closure chart from a MySQL database.

## Project Structure

The project structure is as follows:

    azure-fastapi-mysql-tower-management-appservice/
    │
    ├── .github/
    │ └── main_tmsv-cost-data.yml
    ├── .gitignore
    ├── .env
    ├── data/
    │ └── sunburstData.json
    │ └── gridData.json
    ├── logs/
    │ └── application.log
    ├── src/
    │ └── utility_functions.py
    │ └── functions.py
    │ └── api.py
    │ └── main.py
    ├── requirements.txt
    ├── README.md
    └── LICENSE 



- **.github**: Contains GitHub Actions workflows.
- **.gitignore**: Specifies which files and directories to ignore in the project.
- **.env**: Contains environment variables for configuration.
- **data**: Contains the JSON files `sunburstData.json` and `gridData.json`.
- **logs**: Directory for storing log files.
- **src**: Contains the main application scripts, including utility functions, core functions, API endpoints, and the main FastAPI application script.
- **requirements.txt**: Lists the Python dependencies for the project.
- **README.md**: This file, containing instructions and information about the project.
- **LICENSE**: Contains the Apache license for the project.

### Explanation of Python Files

- **utility_functions.py**: Contains helper functions for tasks such as reading environment variables, setting up database connections, and configuring logging.
- **functions.py**: Contains core functions used by the API endpoints, such as data processing and business logic implementations.
- **api.py**: Defines the API endpoints for the application. This file contains the logic for handling HTTP requests and returning appropriate responses.
- **main.py**: The main FastAPI application script. This file initializes the FastAPI app, includes middleware configurations, and integrates with Sentry for error tracking and performance monitoring.

## Getting Started

### Prerequisites

- Python 3.11
- FastAPI
- Uvicorn
- MySQL

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/hirushiharan/azure-fastapi-mysql-tower-management-appservice.git
    cd azure-fastapi-mysql-tower-management-appservice
    ```

2. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

3. Create a `.env` file in the project root with the following content:

    ```env
    MYSQL_PASSWORD=your_mysql_password
    MYSQL_DATABASE=your_database_name
    MYSQL_USER=your_mysql_user
    MYSQL_HOST=your_mysql_host
    MYSQL_PORT=your_mysql_port
    SENTRY_DSN=your_sentry_dsn_if_applicable
    ```

4. Set up the MySQL database:

    - Create a MySQL database and a table to store the Closure data.
    - Configure the database connection details in your environment variables or `.env` file.

5. Configure [Sentry](https://docs.sentry.io/platforms/python/) for error tracking and performance monitoring by setting the `SENTRY_DSN` environment variable.

### Running the Application

1. Ensure the JSON files `sunburstData.json` and `gridData.json` are present in the `data` directory.
2. Ensure the MySQL database is set up and accessible.
3. Run the application using Uvicorn:

    ```bash
    uvicorn src.main:app --host 0.0.0.0 --port 8000
    ```

4. The application should now be running at `http://127.0.0.1:8000`.

### Testing with Postman

1. **Check if the app is running**

    - **Method**: GET
    - **URL**: `http://127.0.0.1:8000/`
    - **Response**: 
      ```json
      {
          "message": "Tower Management Azure app is running..."
      }
      ```

2. **Get Sunburst Data**

    - **Method**: GET
    - **URL**: `http://127.0.0.1:8000/sunburstData`
    - **Response**: The content of `sunburstData.json`

3. **Get Grid Data**

    - **Method**: GET
    - **URL**: `http://127.0.0.1:8000/gridData`
    - **Response**: The content of `gridData.json`

4. **Get Closure Data**

    - **Method**: GET
    - **URL**: `http://127.0.0.1:8000/closureData`
    - **Response**: The content retrieved from the MySQL database

## Features Available

1. **Enhanced Error Handling**: Added more detailed error handling to provide specific messages and status codes for different error scenarios.
2. **Logging**: Configured custom logging to track events, errors, and important actions within the application.
3. **Environment-Specific Configuration**: Added support for environment-specific settings to better manage different deployment scenarios.
4. **Dependency Injection**: Implemented dependency injection for better modularity and testability.
5. **Database Connection Pooling**: Added database connection pooling to optimize database interactions and improve performance.
6. **Middleware**: Added middleware for tasks such as request validation, authentication, and rate limiting.
7. **API Documentation**: Enhanced the auto-generated API documentation with detailed descriptions and examples.
8. **Sentry Integration**: Configured Sentry for error tracking and performance monitoring.

### Improvements Can be Done

1. **Security**: Include security headers and input validation.
2. **Testing**: Add unit tests for endpoints using `pytest`.

## Notes

- Ensure that the `data` directory and JSON files (`sunburstData.json` and `gridData.json`) are present and correctly named.
- If the JSON files are missing or incorrectly named, the endpoints `/sunburstData` and `/gridData` will return a 404 error with the message `{"error": "File not found"}`.
- Ensure that the MySQL database is properly set up and the connection details are configured.
- If the database connection fails, the `/closureData` endpoint will return a 500 error with the message `{"error": "Database connection failed"}`.
- If Sentry is not properly configured, error tracking and performance monitoring will not be available.

## API Documentation

### Endpoint Documentation

You can view the interactive API documentation provided by FastAPI at http://127.0.0.1:8000/docs. This documentation includes details about all endpoints.

### FastAPI Documentation

Refer to [FastAPI documentation](https://fastapi.tiangolo.com/reference/) for more information.

## License

This project is licensed under the Apache License. See the LICENSE file for details.
