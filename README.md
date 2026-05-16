# Requirements Management Portal

Full-stack requirements management app built with React, FastAPI, and PostgreSQL. Users can sign up, log in, and manage requirement records from a protected frontend workspace.

## Features

- User signup and login
- JWT generation after authentication
- Auth session stored in `localStorage`
- Protected frontend `/requirements` route
- Requirements table with status badges
- Add Requirement modal
- Refresh action for the requirements table
- Status summary counts for total, open, processed, and obsolete requirements
- Loading and error states
- PostgreSQL schemas separated into `auth` and `app`
- bcrypt password hashing
- Parameterized SQL queries with pg8000
- Pydantic request validation
- Database-level status validation with a `CHECK` constraint 

## feature added as extra 
- Pagination with `10`, `20`, `50`, and `All` page-size options

## future improvement suggestions:
- API level filtering of requirements based on 'Total', 'Open', 'Processed' and 'obsolete'.
- DELETE and PATCH APIs for requirements.

## Tech Stack

- Frontend: React, Vite, react-router-dom
- Backend: FastAPI, Python, Uvicorn
- Database: PostgreSQL
- Security: bcrypt, JWT
- Database driver: pg8000

## Project Structure

```text
repo/
|-- backend/
|   |-- app/
|   |   |-- config/
|   |   |   `-- settings.py
|   |   |-- database/
|   |   |   `-- connection.py
|   |   |-- models/
|   |   |   |-- auth_models.py
|   |   |   `-- requirement_models.py
|   |   |-- routes/
|   |   |   |-- auth.py
|   |   |   `-- requirements.py
|   |   `-- services/
|   |       `-- security.py
|   |-- main.py
|   `-- requirements.txt
|-- frontend/
|   |-- src/
|   |   |-- App.jsx
|   |   |-- api.js
|   |   |-- main.jsx
|   |   `-- styles.css
|   |-- index.html
|   `-- package.json
|-- mock_requirements.csv
|-- schema.sql
`-- README.md
```

## Database

The PostgreSQL database uses two schemas:

- `auth`: stores user accounts
- `app`: stores requirements

`schema.sql` creates:

- `auth.users`
- `app.requirements`

Requirement statuses are constrained at the database level:

```sql
CHECK (status IN ('open', 'processed', 'obsolete'))
```

This means PostgreSQL rejects invalid status values even if data is inserted outside the API.

## API Endpoints

Authentication:

```text
POST /auth/signup
POST /auth/login
```

Requirements:

```text
GET    /requirements?page=1&limit=10
GET    /requirements/all
POST   /requirements
```

The main requirements list endpoint returns pagination metadata:

```json
{
  "requirements": [],
  "total": 121,
  "page": 1,
  "limit": 10,
  "total_pages": 13,
  "status_counts": {
    "open": 40,
    "processed": 40,
    "obsolete": 41
  }
}
```

The frontend defaults to `limit=10`. The `All` dropdown option requests all rows in one response by using the current total as the limit.

## Prerequisites

- Python 3.14 or above
- Node.js 22 or above
- PostgreSQL

## Database Setup

From the project root, create a database:

```powershell
psql -U postgres
```

Inside the PostgreSQL prompt:

```sql
CREATE DATABASE interntask_db;
\q
```

Load the schema:

```powershell
psql -U postgres -d interntask_db -f schema.sql
```

Optional: load the mock requirements:

```powershell
psql -U postgres -d interntask_db -c "\copy app.requirements(title, description, status) FROM 'mock_requirements.csv' WITH (FORMAT csv, HEADER true);"
```

Or open PostgreSQL manually:

```powershell
psql -U postgres -d interntask_db
```

Inside the PostgreSQL prompt, run this from the project root path:

```sql
\copy app.requirements(title, description, status) FROM 'mock_requirements.csv' WITH (FORMAT csv, HEADER true);
```

## Backend Setup

Use Python 3.14 or above for the backend.

Go to the backend folder:

```powershell
cd backend
```

Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create `backend/.env`:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=interntask_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password
PORT=8000
SECRET_KEY=replace_with_a_long_random_secret
DEBUG=True
```

Run the backend:

```powershell
.\venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Backend:

```text
http://127.0.0.1:8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```

## Frontend Setup

Use Node.js 22 or above for the frontend.

Open a second terminal from the project root:

```powershell
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

Optional `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
```

## Running The App

1. Start PostgreSQL.
2. Load `schema.sql`.
3. Start the backend on `http://127.0.0.1:8000`.
4. Start the frontend on `http://localhost:5173`.
5. Open `/signup` and create an account.
6. Log in from `/login`.
7. Use the `/requirements` workspace to view and add requirements.

## Frontend Routes

```text
/login
/signup
/requirements
```

Unauthenticated users are redirected to `/login` before accessing `/requirements`.

## Validation

Signup:

- Email must be valid.
- Username must be 3 to 255 characters.
- Password must be at least 6 characters.

Requirement:

- Title is required and max 255 characters.
- Description is optional.
- Status must be `open`, `processed`, or `obsolete`.

Status validation is enforced in two places:

- API level: Pydantic `StatusEnum`
- Database level: PostgreSQL `CHECK` constraint

## Smoke Tests

Health check:

```powershell
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "message": "Server is running"
}
```

Paginated requirements:

```powershell
curl "http://127.0.0.1:8000/requirements?page=1&limit=10"
```

## Build

Frontend production build:

```powershell
cd frontend
npm run build
```

## Notes

- Requirement SQL uses parameterized values.
- Passwords are never stored as plain text.
- The frontend stores the returned auth token and user details in `localStorage`.
- Restart the backend after changing backend route or model files.
