import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from cobwebai.models.base import Base

# URL к тестовой базе данных
TEST_DATABASE_URL = "postgresql+psycopg2://postgres:Anton2003@localhost:5432/test"

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)