from contextlib import asynccontextmanager
from typing import Union, Optional, Annotated
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, create_engine, SQLModel, select, Field
from app import settings
from fastapi.middleware.cors import CORSMiddleware
from typing import AsyncGenerator

class Todo(SQLModel, table = True):
    id : Optional[int] = Field(primary_key=True)
    content : str = Field(index=True)

class TodoResponse(SQLModel):
    id : int
    content : str

class CreateTodo(SQLModel):
    content : str

connection_string = str(settings.DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg"
)

engine = create_engine(
    connection_string, connect_args={}, pool_recycle=300
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI)-> AsyncGenerator[None, None]:
    print("Creating tables..")
    create_db_and_tables()
    yield

app  : FastAPI = FastAPI(lifespan = lifespan,title = "Todo App with poetry",
        version="0.0.1")
origins=[
            
                 
                  "http://127.0.0.1:8000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Dependancy injection

def get_session():
    with Session(engine)as session:
        yield session

#test 
@app.get("/")
def test_read_root():
    return {"Hello": "World"}        


#get all todo
@app.get("/todos/", response_model=list[Todo])
def read_all_todos(session: Annotated[Session, Depends(get_session)]):
    todos = session.exec(select(Todo)).all()
    return todos

#get todo by id
@app.get("/todo/{id}", response_model=TodoResponse)
def get_todo_by_id(id : int, session : Annotated[Session, Depends(get_session)]):
    todo = session.get(Todo, id)
    if not todo :
        raise HTTPException(status_code=404, detail= " todo not found")
    return todo

#post todo
@app.post("/todos/", response_model=TodoResponse)
def post_todos(todo: CreateTodo, session: Annotated[Session, Depends(get_session)]):
    new_todo = Todo(content=todo.content)
    session.add(new_todo)
    session.commit()
    session.refresh(new_todo)
    return new_todo

#update a todo
@app.put("/todo/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo:CreateTodo, session : Annotated[Session, Depends(get_session)]):
    todo_query = session.exec(select(Todo).where(Todo.id == todo_id)).first()
    if not todo_query:
        raise HTTPException(status_code = 404, detail = "Todo not found")
    todo_query.content = todo.content
    session.commit()
    session.refresh(todo_query)
    return todo_query

#Delete todo
@app.delete("/todo/{todo_id}")
def delete_todo(todo_id: int, session: Annotated[Session, Depends(get_session)]):
    todo_query = session.exec(select(Todo).where(Todo.id == todo_id)).first()
    if not todo_query:
        raise HTTPException(status_code=404, detail="Todo not found")
    session.delete(todo_query)
    session.commit()
    return {"message": "Todo deleted successfully"}
    