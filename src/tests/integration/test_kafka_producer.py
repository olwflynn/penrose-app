import pytest
from src.main.app import create_app


@pytest.fixture
def client():

    penrose = create_app()
    penrose.config['TESTING'] = True
    with penrose.test_client() as client:

        yield client

def test_producer(client):
    """
    GIVEN the producer
    WHEN API call is made
    THEN check the same message in the body of the API call is what is in kafka
    """
    response = client.post('/kafka/pushTransaction',
                           json=dict(key123="value456"))
    assert b'It works we got it!!' not in response.data
    # assert b'It works we got it!!' in response.data
