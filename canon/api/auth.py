import datetime
import logging
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from canon.db import get_session
from canon.models.base import PydanticBase
from canon.models.user import User

from .messages import set_message_headers

logger = logging.getLogger(__name__)
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt_sha256", "bcrypt"], deprecated="auto"
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

SECRET_KEY = "CHANGE_ME_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

router = APIRouter(prefix="/auth", tags=["auth"])

class Token(PydanticBase):
    access_token: str
    token_type: str

class TokenData(PydanticBase):
    username: Optional[str] = None

class UserCreate(PydanticBase):
    username: str
    email: EmailStr
    password: str

class UserOut(PydanticBase):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    is_admin: bool


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(
    data: dict,
    expires_delta: Optional[datetime.timedelta] = None,
) -> str:
    to_encode = data.copy()
    # Use timezone-aware UTC datetimes to avoid deprecation warnings and
    # encourage explicit timezone handling (Python 3.14+).
    expire = datetime.datetime.now(datetime.UTC) + (
        expires_delta or datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()

async def authenticate_user(
    db: AsyncSession, username: str, password: str
) -> Optional[User]:
    user = await get_user_by_username(db, username)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


@router.post("/register", response_model=UserOut)
async def register(
    user_in: UserCreate,
    session: Annotated["AsyncSession", Depends(get_session)],
    response: Response,
) -> User:
    db = session
    result = await db.execute(
        User.__table__.select().where(
            (User.username == user_in.username) | (User.email == user_in.email)
        )
    )
    if result.first():
        raise HTTPException(
            status_code=400,
            detail="Username or email already registered",
        )

    try:
        password_hash = get_password_hash(user_in.password)
    except ValueError as err:
        # Return a client-friendly 400 if the hashing backend rejects the password
        logger.warning("Password hashing failed: %s", err)
        raise HTTPException(
            status_code=400,
            detail=str(err),
        ) from err

    user = User(
        username=user_in.username,
        email=user_in.email,
        password_hash=password_hash,
    )
    db.add(user)
    try:
        await db.commit()
        await db.refresh(user)
    except IntegrityError as err:
        # Handle race-condition where another request inserted the same
        # username/email between our existence check and commit.
        await db.rollback()
        logger.warning("IntegrityError on user register: %s", err)
        raise HTTPException(
            status_code=400,
            detail="Username or email already registered",
        ) from err

    # Add a friendly success message header for the frontend toast system
    set_message_headers(
        response,
        "Registration successful. Please check your email to verify if required.",
        "success",
    )

    return user


@router.post("/login", response_model=Token)
async def login(
    request: Request, session: Annotated["AsyncSession", Depends(get_session)]
) -> Token:
    form = await request.form()
    username = form.get("username")
    password = form.get("password")
    if not isinstance(username, str) or not isinstance(password, str):
        raise HTTPException(status_code=400, detail="Invalid login form")
    db = session
    logger.debug("Login attempt for username=%s", username)
    user = await authenticate_user(db, username, password)
    if not user:
        # Fallback: try using the same public function so tests that monkeypatch
        # `get_user_by_username` will be respected. Only if the public helper
        # returns a user do we attempt verification.
        user2 = await get_user_by_username(db, username)
        if user2 and verify_password(password, user2.password_hash):
            logger.debug("Fallback authentication succeeded for username=%s", username)
            user = user2
        else:
            logger.debug("Authentication failed for username=%s", username)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
        )
    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token, token_type="bearer")

@router.get("/me", response_model=UserOut)
async def read_users_me(
    session: Annotated["AsyncSession", Depends(get_session)],
    token: str = Depends(oauth2_scheme),
) -> User:
    db = session
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not isinstance(username, str):
            raise credentials_exception
    except JWTError as err:
        raise credentials_exception from err
    user = await get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user
