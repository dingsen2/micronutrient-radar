import os
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the project root directory to the Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

# Add the backend directory to the Python path
backend_dir = str(Path(__file__).parent.parent / 'backend')
sys.path.insert(0, backend_dir) 

# Ensure models are imported so that Base.metadata knows about them
from backend.app.models import models  # noqa
from backend.app.db.base_class import Base

@pytest.fixture(scope="session")
def test_engine():
    # Use an in-memory SQLite database for testing
    engine = create_engine("sqlite:///./test.db")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    os.remove("test.db")

@pytest.fixture(scope="function")
def db_session(test_engine):
    connection = test_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = Session()
    yield session
    session.close()
    transaction.rollback()
    connection.close()

# Override the get_db dependency for tests
@pytest.fixture(scope="function")
def client_with_db(db_session):
    from fastapi.testclient import TestClient
    from backend.app.main import app
    from backend.app.db.session import get_db

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear() 