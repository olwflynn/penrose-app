import pytest
from src.main.app import create_app

@pytest.fixture
def client():

    penrose = create_app()
    penrose.config['TESTING'] = True
    with penrose.test_client() as client:

        yield client