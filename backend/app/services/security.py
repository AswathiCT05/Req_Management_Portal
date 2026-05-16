import bcrypt
import jwt
from datetime import datetime, timedelta
from app.config.settings import settings


# Hashes user passwords with bcrypt before database storage.
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


# Checks a login password against the stored bcrypt hash.
def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False


# Creates a signed JWT for the authenticated user session.
def create_jwt_token(user_id: int, email: str, expires_in_days: int = None) -> str:
    if expires_in_days is None:
        expires_in_days = settings.JWT_EXPIRATION_DAYS
    
    payload = {
        'user_id': user_id,
        'email': email,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(days=expires_in_days)
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token


# Decodes and validates a JWT token.
def verify_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
