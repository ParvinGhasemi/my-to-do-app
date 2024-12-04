from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from ..database import Base
from ..main import app
from ..routers.todos import get_db, get_current_user
from fastapi.testclient import TestClient
from fastapi import status
import pytest
from ..models import Todos


SQLALCHEMY_DATABASE_URL = 'sqlite:///./testdb.db'

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False}, poolclass=StaticPool)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def override_get_current_user():
    return {'username': 'paptest', 'id': 1, 'user_role': 'admin'}
        
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)

@pytest.fixture
def test_todo():
    todo = Todos(title='Test Todo', description='Test Todo Description', priority=5, complete=False, owner_id=1)
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()

# tests
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
    