from fastapi import Depends
from fastapi.requests import Request
from sqlmodel import create_engine, Session

from config.database_config import DATABASE_URL
from services.security_service.security import (
    oauth2_scheme,
)
from services.security_service.security_data_models import (
    UserData,
)

engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=100,
)


def get_session(
    request: Request,
    user_data: UserData = Depends(oauth2_scheme),
):
    with Session(engine) as session:
        yield session
