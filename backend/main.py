from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.routes import auth, requirements


app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION
)


# Allows the React frontend to call the FastAPI backend during development.
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Registers authentication and requirements API route groups.
app.include_router(auth.router)
app.include_router(requirements.router)


# Confirms that the backend server is reachable.
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "Server is running"}


# Provides basic API entry links.
@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": "Welcome to Requirements Intake API",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG
    )
