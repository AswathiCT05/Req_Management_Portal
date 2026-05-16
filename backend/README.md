# Backend

FastAPI backend for the Requirements Intake app.

## Prerequisites

- Python 3.14 or above
- PostgreSQL

## Structure

```text
backend/
|-- app/
|   |-- config/
|   |   `-- settings.py
|   |-- database/
|   |   `-- connection.py
|   |-- models/
|   |   |-- auth_models.py
|   |   `-- requirement_models.py
|   |-- routes/
|   |   |-- auth.py
|   |   `-- requirements.py
|   `-- services/
|       `-- security.py
|-- main.py
|-- requirements.txt
`-- .env
```

## Run

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
.\venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```
