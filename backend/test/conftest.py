import os
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from typing import Generator

# Add the project root directory to the Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

# Add the backend directory to the Python path
backend_dir = str(Path(__file__).parent.parent / 'backend')
sys.path.insert(0, backend_dir) 

# Ensure models are imported so that Base.metadata knows about them
from app.models import models  # noqa
from app.db.base_class import Base
from app.core.config import settings
from app.models.user import User
from app.api import deps

# Use the same database URL as the main application
SQLALCHEMY_DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db() -> Generator:
    Base.metadata.create_all(bind=engine)
    yield
    # Drop all tables with CASCADE to handle foreign key constraints
    with engine.connect() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE;"))
        conn.execute(text("CREATE SCHEMA public;"))
        conn.commit()

@pytest.fixture(scope="function")
def db_session(db: Generator) -> Generator:
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    # Begin a nested transaction. This allows commits within the app to work,
    # while the outer transaction (managed by 'transaction') is rolled back at the end.
    # nested = session.begin_nested() # Removed nested transaction for simpler management
    yield session

    # Rollback the outer transaction to ensure a clean state for the next test.
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def mock_current_user(test_user: User):
    # This needs to match the structure of your actual User model being returned by get_current_user
    class MockUser:
        id = test_user.id
        email = test_user.email
        demographics = test_user.demographics
        settings = test_user.settings

    return MockUser()

# Override the get_db dependency for tests
@pytest.fixture(scope="function")
def client_with_db(db_session, mock_current_user):
    from fastapi.testclient import TestClient
    from app.main import app # Corrected import
    from app.db.session import get_db # Corrected import

    # Ensure the app uses the same db_session instance for all test operations
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[deps.get_current_user] = lambda: mock_current_user

    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear() 