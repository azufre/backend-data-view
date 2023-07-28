import data.crud as crud
import data.models as models
import polars as pl
from data.database import engine
from data.schemas import AuthResponse, UserAuth
from dependencies import get_current_user, get_db
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from services.data_service import DataService
from sqlalchemy.orm import Session
from utils import (create_access_token, create_refresh_token,
                   get_hashed_password, verify_password)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """
    Startup event handler.

    Initializes the Redis backend for FastAPI Cache 
    and connects to the Redis server.

    Returns:
    None
    """
    # Connect to the Redis server using aioredis
    redis = aioredis.from_url("redis://redis")

    # Initialize FastAPI Cache with RedisBackend
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")


@app.get('/', response_class=RedirectResponse, include_in_schema=False)
async def docs():
    """
    Redirect users to the '/docs' endpoint for API documentation.
    """
    return RedirectResponse(url='/docs')


@app.post('/login', summary="Create access and refresh tokens for user", response_model=AuthResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate the user and create access and refresh tokens upon successful login.

    Args:
        form_data (OAuth2PasswordRequestForm): The form data containing the user's username and password.
        db (Session): The database session to access user data.

    Returns:
        dict: An object containing user details along with access and refresh tokens.

    Raises:
        HTTPException(400): If the username or password is incorrect.
    """
    user = crud.get_user_by_username(db, form_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password"
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password"
        )

    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "access_token": create_access_token(user.username),
        "refresh_token": create_refresh_token(user.username),
    }


@app.post('/signup', summary="Create new user", response_model=AuthResponse)
async def create_user(data: UserAuth, db: Session = Depends(get_db)):
    """
    Create a new user account.

    Args:
        data (UserAuth): The user data including email, username, and password.
        db (Session): The database session to store the new user data.

    Returns:
        dict: An object containing user details along with access and refresh tokens.

    Raises:
        HTTPException(400): If the provided email or username already exists in the database.
    """
    user = crud.get_user_by_email(db, data.email)
    user_username = crud.get_user_by_username(db, data.username)

    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    if user_username is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username already exists"
        )

    data.password = get_hashed_password(data.password)

    user = crud.create_user(db=db, user=data)

    response = {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "access_token": create_access_token(user.username),
        "refresh_token": create_refresh_token(user.username),
    }

    return response


@app.get("/get_std_data")
async def get_std_data(data_service: DataService = Depends(), user: models.User = Depends(get_current_user)):
    """
    FastAPI endpoint to get standard deviations of features grouped by class.

    Parameters:
    - data_service (DataService, optional): An instance of the DataService class. 
    If not provided, it will be automatically resolved using Depends.

    Returns:
    dict: A dictionary containing standard deviations of features grouped by class. 
    The keys are feature names with "_std" suffix, 
    and the values are the corresponding standard deviations.
    """
    # Get data from the DataService class
    df: pl.LazyFrame = await data_service.get_data_from_file()

    # Clean the data by removing rows with null values
    df = data_service.clean_data(df)

    # Calculate standard deviations of features grouped by class
    aggregations = df.groupby("class").agg(
        **{col: pl.col(col).std().alias(f"{col}_std") for col in df.columns[0:-2]}
    )

    # Materialize the lazy DataFrame
    aggregations = aggregations.collect()

    return aggregations.to_dicts()


@app.get("/get_mean_data")
async def get_mean_data(data_service: DataService = Depends(), user: models.User = Depends(get_current_user)):
    """
    FastAPI endpoint to get mean values of features grouped by class.

    Parameters:
    - data_service (DataService, optional): An instance of the DataService class. 
      If not provided, it will be automatically resolved using Depends.

    Returns:
    dict: A dictionary containing mean values of features grouped by class. 
    The keys are feature names with "_mean" suffix, 
    and the values are the corresponding mean values.
    """
    # Get data from the DataService class
    df: pl.LazyFrame = await data_service.get_data_from_file()

    # Clean the data by removing rows with null values
    df = data_service.clean_data(df)

    # Calculate mean values of features grouped by class
    aggregations = df.groupby("class").agg(
        **{col: pl.col(col).mean().alias(f"{col}_mean") for col in df.columns[0:-2]}
    )

    # Materialize the lazy DataFrame
    aggregations = aggregations.collect()

    return aggregations.to_dicts()
