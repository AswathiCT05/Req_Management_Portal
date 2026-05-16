# Requirements Management Portal

Full-stack web application built for the Intern Task - Full Stack Exercise. The app provides user authentication and a protected requirements management page where logged-in users can view existing requirements and add new ones.

## Features

- Login page for existing users
- Signup page for new users
- Protected `/requirements` page
- Authentication state stored in `localStorage`
- Requirements table with status badges
- Add requirement form
- Pagination for larger requirement lists
- Loading and error states
- PostgreSQL database with separated `auth` and `app` schemas
- bcrypt password hashing
- Parameterized SQL queries
- Pydantic and database-level status validation

## Tech Stack

- Frontend: React, Vite, react-router-dom
- Backend: FastAPI, Python
- Database: PostgreSQL
- Security: bcrypt password hashing, JWT tokens

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
|   |-- requirements.txt
|   `-- README.md
|-- frontend/
|   |-- src/
|   |   |-- App.jsx
|   |   |-- api.js
|   |   |-- main.jsx
|   |   `-- styles.css
|   |-- index.html
|   |-- package.json
|   `-- serve.py
|-- schema.sql
|-- mock_requirements.csv
`-- README.md
```

## Database Design

The database uses PostgreSQL with two fully separate schemas:

- `auth` stores user authentication data.
- `app` stores requirement data.

The schemas are independent. There are no foreign keys or relationships between `auth.users` and `app.requirements`.

Tables created by `schema.sql`:

- `auth.users`
- `app.requirements`

Requirement status values are enforced in the database with a `CHECK` constraint:

```sql
status IN ('open', 'processed', 'obsolete')
```

## API Endpoints

Authentication:

- `POST /auth/signup`
- `POST /auth/login`

Requirements:

- `GET /requirements`
- `POST /requirements`

Additional implemented endpoints:

- `PATCH /requirements/{requirement_id}`
- `DELETE /requirements/{requirement_id}`

## Important Rules Covered

- No plain-text passwords: passwords are hashed with bcrypt before storage.
- No SQL string concatenation for user input: SQL values are passed through parameterized queries.
- Strict schema separation: users are stored in `auth.users`, requirements are stored in `app.requirements`.
- Proper validation: Pydantic validates API input, including allowed status values.
- Proper error handling: duplicate email, invalid login, invalid status, missing records, and server errors return clear API responses.

## Prerequisites

Install these before running the project:

- Python 3.10 or later
- Node.js 18 or later
- PostgreSQL

## Database Setup

Open PowerShell or a terminal from the project root.

Create the database:

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

## Backend Setup

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
python main.py
```

Or run it with uvicorn:

```powershell
.\venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

## Frontend Setup

Open a second terminal from the project root.

Go to the frontend folder:

```powershell
cd frontend
```

Install dependencies:

```powershell
npm install
```

Run the frontend development server:

```powershell
npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

Optional `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
```

## Running The Full App

1. Start PostgreSQL.
2. Run the backend on `http://127.0.0.1:8000`.
3. Run the frontend on `http://localhost:5173`.
4. Open `/signup` and create a new account.
5. Log in from `/login`.
6. After login, the app redirects to `/requirements`.

## Frontend Routes

- `/login`: login page
- `/signup`: account creation page
- `/requirements`: protected requirements page

If a user is not logged in and tries to open `/requirements`, the app redirects to `/login`.

## Validation Details

Signup validation:

- Email must be valid.
- Username must be at least 3 characters.
- Password must be at least 6 characters.

Requirement validation:

- Title is required.
- Description is optional.
- Status must be one of `open`, `processed`, or `obsolete`.

Status validation exists in both places:

- Backend API using Pydantic enum validation
- PostgreSQL using a `CHECK` constraint

## Smoke Test

With the backend running:

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

## Completion Status

All required parts from the task description are implemented:

- Backend authentication APIs
- Backend requirements APIs
- PostgreSQL schema separation
- bcrypt password hashing
- Parameterized SQL queries
- Pydantic and database validation
- React login/signup/requirements pages
- Protected route behavior
- localStorage authentication flow
- Loading and error handling

