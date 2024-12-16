import pytest
from todo_app import app, todo_collection
from flask_pymongo import PyMongo

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/test_todo_db'
    with app.test_client() as client:
        with app.app_context():
            global mongo
            mongo = PyMongo(app)
            mongo.db.todos.delete_many({})  # Clear test database
        yield client

def test_add_task(client):
    response = client.post('/todo', json={"title": "Test Task", "description": "Test Description"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["title"] == "Test Task"
    assert data["description"] == "Test Description"

def test_get_tasks(client):
    client.post('/todo', json={"title": "Task 1"})
    response = client.get('/todo')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) > 0

def test_edit_task(client):
    response = client.post('/todo', json={"title": "Task to Edit"})
    task_id = response.get_json()["_id"]
    response = client.put(f'/todo/{task_id}', json={"title": "Edited Task"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["title"] == "Edited Task"

def test_delete_task(client):
    response = client.post('/todo', json={"title": "Task to Delete"})
    task_id = response.get_json()["_id"]
    response = client.delete(f'/todo/{task_id}')
    assert response.status_code == 200

def test_delete_all_tasks(client):
    client.post('/todo', json={"title": "Task 1"})
    client.post('/todo', json={"title": "Task 2"})
    response = client.delete('/todo')
    assert response.status_code == 200
