from fastapi.testclient import TestClient
from fastapi import FastAPI, Depends
from app import settings
from app.main import app, Todo, get_session
from sqlmodel import SQLModel, Session, create_engine, select

def test_read_main():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

def write_todo():
    
    connection_str = str(settings.TEST_DATABASE_URL).replace(
        "postgresql", "postgresql+psycopg"
    )

    engine = create_engine(
        connection_str, connect_args={"sslmode": "require"}, pool_recycle=300
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:

        def get_session_override():
            return session

        app.dependency_overrides[get_session] = get_session_override

        client = TestClient(app=app)

        todo_content = "buy clothes"

        response = client.post("/todos/",
        json={"content": todo_content}
                                )

        data = response.json()

        assert response.status_code == 200
        assert data["content"] == todo_content


def read_todo_main():
   
    connection_str = str(settings.TEST_DATABASE_URL).replace(
        "postgresql", "postgresql+psycopg"
    )

    engine = create_engine(
        connection_str, connect_args={"sslmode": "require"}, pool_recycle=300
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:

        def get_session_override():
            return session

        app.dependency_overrides[get_session] = get_session_override

        client = TestClient(app=app)

        
        response = client.get("/todos/")

        assert response.status_code == 200
        

def read_todo_main_by_id():
   
    connection_str = str(settings.TEST_DATABASE_URL).replace(
        "postgresql", "postgresql+psycopg"
    )

    engine = create_engine(
        connection_str, connect_args={"sslmode": "require"}, pool_recycle=300
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:

        def get_session_override():
            return session

        app.dependency_overrides[get_session] = get_session_override

        client = TestClient(app=app)
  
        response = client.get("/todo/1")  
        assert response.status_code == 200
        assert response.json()
   

def test_update_todo():

    connection_str = str(settings.TEST_DATABASE_URL).replace(
        "postgresql", "postgresql+psycopg"
    )

    engine = create_engine(
        connection_str, connect_args={"sslmode": "require"}, pool_recycle=300
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:

        def get_session_override():
            return session

        app.dependency_overrides[get_session] = get_session_override

        client = TestClient(app=app)

        test_todo = Todo(content="Test Todo")
        session.add(test_todo)
        session.commit()

        
        updated_content = "Updated Todo"
        response = client.put(f"/todo/{test_todo.id}", json={"content": updated_content})
        
        assert response.status_code == 200
        assert response.json()["content"] == updated_content

        
def test_delete_todo():

    connection_str = str(settings.TEST_DATABASE_URL).replace(
        "postgresql", "postgresql+psycopg"
    )

    engine = create_engine(
        connection_str, connect_args={"sslmode": "require"}, pool_recycle=300
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:

        def get_session_override():
            return session

        app.dependency_overrides[get_session] = get_session_override

        client = TestClient(app=app)
    
    test_todo = Todo(content="Test Todo")
    session.add(test_todo)
    session.commit()

    
    response = client.delete(f"/todo/{test_todo.id}")
    
    assert response.status_code == 200
    assert response.json() == {"message": "Todo deleted successfully"}
       