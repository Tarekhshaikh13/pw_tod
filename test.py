import pytest
from main import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_add_todo(client):
    response = client.post('/todos', json={'todo': 'Learn Flask'})
    assert response.status_code == 201
    assert response.json['message'] == 'Todo added'

def test_get_todos(client):
    client.post('/todos', json={'todo': 'Learn Flask'})
    response = client.get('/todos')
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0] == 'Learn Flask'

def test_delete_todo(client):
    client.post('/todos', json={'todo': 'Learn Flask'})
    response = client.delete('/todos/0')
    assert response.status_code == 200
    assert response.json['message'] == 'Todo deleted'

def test_update_todo(client):
    client.post('/todos', json={'todo': 'Learn Flask'})
    response = client.put('/todos/0', json={'todo': 'Learn Python'})
    assert response.status_code == 200
    assert response.json['message'] == 'Todo updated'

def test_invalid_todo(client):
    response = client.post('/todos', json={})
    assert response.status_code == 400
    assert response.json['error'] == 'Todo is required'

