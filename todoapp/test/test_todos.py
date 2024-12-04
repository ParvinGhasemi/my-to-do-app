from ..routers.todos import get_db, get_current_user
from fastapi import status
from ..models import Todos
from .utils import *
        
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_read_all_authenticated(test_todo):
    response = client.get('/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'id': 1, 'priority': 5, 'owner_id': 1, 'title': 'Test Todo', 'description': 'Test Todo Description', 'complete': False}]
    
    
def test_read_one_authenticated(test_todo):
    response = client.get('/todos/1')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'id': 1, 'priority': 5, 'owner_id': 1, 'title': 'Test Todo', 'description': 'Test Todo Description', 'complete': False}


def test_read_one_authenticated_not_found(test_todo):
    response = client.get('/todos/999')
    assert response.status_code == status.HTTP_404_NOT_FOUND    # or simplu: == 404
    assert response.json() == {'detail': 'To-do not found.'}
    
    
# test create new todo
def test_create_todo(test_todo):
    request_data = {
        'title': 'New Todo',
        'description': 'New Todo Description',
        'priority': 5,
        'complete': False
    }
    response = client.post('/todos', json=request_data)
    assert response.status_code == status.HTTP_201_CREATED
    
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 2).first()
    assert model.title == request_data['title'] # or == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.complete == request_data.get('complete')
    
    
def test_update_todo(test_todo):
    request_data = {
        'title': 'Updated Todo',
        'description': 'Updated Todo Description',
        'priority': 4,
        'complete': True,
    }
    
    response = client.put('/todos/1', json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.complete == request_data.get('complete')
    

def test_update_todo_not_found(test_todo):
    request_data = {
        'title': 'Updated Todo',
        'description': 'Updated Todo Description',
        'priority': 4,
        'complete': True,
    }
    
    response = client.put('/todos/999', json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'To-do not found.'}
    
    
    
def test_delete_todo(test_todo):
    response = client.delete('/todos/1')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None
    


def test_delete_todo_not_found(test_todo):
    response = client.delete('/todos/999')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'To-do not found.'}