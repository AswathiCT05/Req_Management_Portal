from pydantic import BaseModel, EmailStr, Field
from typing import Optional


# Validates signup input from the frontend.
class SignUpRequest(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=6)
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "password": "securepass123"
            }
        }


# Validates login input from the frontend.
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepass123"
            }
        }


# Shapes the successful auth response returned to the frontend.
class AuthResponse(BaseModel):
    id: int
    email: str
    username: str
    token: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "username": "johndoe",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


# Shapes API error responses.
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Email already registered",
                "error_code": "EMAIL_EXISTS"
            }
        }
