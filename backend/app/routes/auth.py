from fastapi import APIRouter, HTTPException, status
from app.models.auth_models import SignUpRequest, LoginRequest, AuthResponse, ErrorResponse
from app.database.connection import execute_query
from app.services.security import hash_password, verify_password, create_jwt_token
import pg8000.dbapi

router = APIRouter(prefix="/auth", tags=["Authentication"])


# Creates a new user with a bcrypt password hash and JWT session token.
@router.post(
    "/signup",
    response_model=AuthResponse,
    responses={
        400: {"model": ErrorResponse},
        409: {"model": ErrorResponse}
    }
)
def signup(request: SignUpRequest):
    try:
        existing_user = execute_query(
            "SELECT id FROM auth.users WHERE email = %s",
            (request.email,),
            fetch_one=True
        )
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        
        password_hash = hash_password(request.password)
        
        result = execute_query(
            """
            INSERT INTO auth.users (email, username, password_hash)
            VALUES (%s, %s, %s)
            RETURNING id, email, username
            """,
            (request.email, request.username, password_hash),
            fetch_one=True
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        user_id = result['id']
        
        token = create_jwt_token(user_id, request.email)
        
        return AuthResponse(
            id=user_id,
            email=result['email'],
            username=result['username'],
            token=token
        )
    
    except HTTPException:
        raise
    except pg8000.dbapi.IntegrityError as e:
        if 'email' in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        elif 'username' in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Signup failed"
        )
    except Exception as e:
        print(f"Signup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error during signup"
        )


# Authenticates a user and returns a JWT session token.
@router.post(
    "/login",
    response_model=AuthResponse,
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse}
    }
)
def login(request: LoginRequest):
    try:
        user = execute_query(
            "SELECT id, email, username, password_hash FROM auth.users WHERE email = %s",
            (request.email,),
            fetch_one=True
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not verify_password(request.password, user['password_hash']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid password"
            )
        
        token = create_jwt_token(user['id'], user['email'])
        
        return AuthResponse(
            id=user['id'],
            email=user['email'],
            username=user['username'],
            token=token
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error during login"
        )
