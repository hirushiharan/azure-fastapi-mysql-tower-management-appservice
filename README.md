# Azure FastAPI MySQL Tower Management AppService

This FastAPI application serves as a backend for managing and retrieving data for a Tower Management system. It provides endpoints to check if the app is running, and to fetch data for Sunburst and Grid charts from JSON files.

## Endpoints

- **GET /**: Returns a message indicating that the Tower Management Azure app is running.
- **GET /sunburstData**: Returns the data for the Sunburst chart from a JSON file.
- **GET /gridData**: Returns the data for the Grid chart from a JSON file.

## Project Structure

The project structure is as follows:

    azure-fastapi-mysql-tower-management-appservice/
    │
    ├── data/
    │ └── sunburstData.json
    │ └── gridData.json
    ├── main.py
    ├── .gitignore
    ├── LICENSE
    ├── requirements.txt
    └── README.md 


- **data**: This directory contains the JSON files `sunburstData.json` and `gridData.json`.
- **main.py**: This is the main FastAPI application script.
- **.gitignore**: This file specifies which files and directories to ignore in the project.
- **LICENSE**: This file contains the Apache license for the project.
- **requirements.txt**: This file lists the Python dependencies for the project.
- **README.md**: This file, containing instructions and information about the project.

## Getting Started

### Prerequisites

- Python 3.7+
- FastAPI
- Uvicorn

### Installation

1. Clone the repository:

    ```bash
    git clone <repository-url>
    cd azure-fastapi-mysql-tower-management-appservice
    ```

2. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

1. Ensure the JSON files `sunburstData.json` and `gridData.json` are present in the `data` directory.
2. Run the application using Uvicorn:

    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```

3. The application should now be running at `http://127.0.0.1:8000`.

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

## Notes

- Ensure that the `data` directory and JSON files (`sunburstData.json` and `gridData.json`) are present and correctly named.
- If the JSON files are missing or incorrectly named, the endpoints `/sunburstData` and `/gridData` will return a 404 error with the message `{"error": "File not found"}`.

## API Documentation

### Endpoint Documentation

You can view the interactive API documentation provided by FastAPI at http://127.0.0.1:8000/docs. This documentation includes details about all three endpoints.

### FastAPI Documentation

You can reffer [FastAPI](https://fastapi.tiangolo.com/reference/) documentation for more information.

## License

This project is licensed under the Apache License. See the LICENSE file for details.
