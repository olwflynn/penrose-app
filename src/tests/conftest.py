import pytest
from src.main.app import create_app

@pytest.fixture
def client():

    penrose = create_app()
    penrose.config['TESTING'] = True
    print(penrose.config)
    with penrose.test_client() as client:

        yield client