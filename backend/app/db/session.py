# db setup and connection function
"""
This module sets up the database connection and session management for the application.
Functions:
    get_session: Provides a SQLAlchemy session for database operations.
Variables:
    engine: SQLAlchemy engine instance connected to the database.
    SessionLocal: SQLAlchemy session factory.
    SessionDep: Dependency for FastAPI to inject a database session.
"""
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session

from app.config.vars import variables

# TODO: remove echo in production
engine = create_engine(variables.DB_STRING)

# Create a session factory for creating new database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# def create_db_and_tables():
#     SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


# Dependency for FastAPI to inject a database session
SessionDep = Annotated[Session, Depends(get_session)]
