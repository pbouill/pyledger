import datetime
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from canon.db import get_session
from canon.models.base import PydanticBase
from canon.models.user import User

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

SECRET_KEY = "CHANGE_ME_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

router = APIRouter(prefix="/api/auth", tags=["auth"])

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
    expire = datetime.datetime.utcnow() + (
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
async def register(user_in: UserCreate) -> User:
    async for _db in get_session():
        db = _db
        break
    else:
        raise RuntimeError("Could not get DB session")
    result = await db.execute(
        User.__table__.select().where(
            (User.username == user_in.username)
            | (User.email == user_in.email)
        )
    )
    if result.first():
        raise HTTPException(
            status_code=400,
            detail="Username or email already registered",
        )
    user = User(
        username=user_in.username,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=Token)
async def login(request: Request) -> Token:
    form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm)
    async for _db in get_session():
        db = _db
        break
    else:
        raise RuntimeError("Could not get DB session")
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
        )
    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token, token_type="bearer")

@router.get("/me", response_model=UserOut)
async def read_users_me(token: str = Depends(oauth2_scheme)) -> User:
    async for _db in get_session():
        db = _db
        break
    else:
        raise RuntimeError("Could not get DB session")
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
