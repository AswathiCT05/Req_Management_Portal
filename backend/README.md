# Backend

FastAPI backend for the Requirements Intake app.

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
.\venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```
