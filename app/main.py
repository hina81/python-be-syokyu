import os
from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.const import TodoItemStatusCode

from .models.item_model import ItemModel
from .models.list_model import ListModel

from fastapi import Depends
from .dependencies import get_db
from sqlalchemy.orm import Session

DEBUG = os.environ.get("DEBUG", "") == "true"

app = FastAPI(
    title="Python Backend Stations",
    debug=DEBUG,
)

if DEBUG:
    from debug_toolbar.middleware import DebugToolbarMiddleware

    # panelsに追加で表示するパネルを指定できる
    app.add_middleware(
        DebugToolbarMiddleware,
        panels=["app.database.SQLAlchemyPanel"],
    )


class NewTodoItem(BaseModel):
    """TODO項目新規作成時のスキーマ."""

    title: str = Field(title="Todo Item Title", min_length=1, max_length=100)
    description: str | None = Field(default=None, title="Todo Item Description", min_length=1, max_length=200)
    due_at: datetime | None = Field(default=None, title="Todo Item Due")


class UpdateTodoItem(BaseModel):
    """TODO項目更新時のスキーマ."""

    title: str | None = Field(default=None, title="Todo Item Title", min_length=1, max_length=100)
    description: str | None = Field(default=None, title="Todo Item Description", min_length=1, max_length=200)
    due_at: datetime | None = Field(default=None, title="Todo Item Due")
    complete: bool | None = Field(default=None, title="Set Todo Item status as completed")


class ResponseTodoItem(BaseModel):
    id: int
    todo_list_id: int
    title: str = Field(title="Todo Item Title", min_length=1, max_length=100)
    description: str | None = Field(default=None, title="Todo Item Description", min_length=1, max_length=200)
    status_code: TodoItemStatusCode = Field(title="Todo Status Code")
    due_at: datetime | None = Field(default=None, title="Todo Item Due")
    created_at: datetime = Field(title="datetime that the item was created")
    updated_at: datetime = Field(title="datetime that the item was updated")


class NewTodoList(BaseModel):
    """TODOリスト新規作成時のスキーマ."""

    title: str = Field(title="Todo List Title", min_length=1, max_length=100)
    description: str | None = Field(default=None, title="Todo List Description", min_length=1, max_length=200)


class UpdateTodoList(BaseModel):
    """TODOリスト更新時のスキーマ."""

    title: str | None = Field(default=None, title="Todo List Title", min_length=1, max_length=100)
    description: str | None = Field(default=None, title="Todo List Description", min_length=1, max_length=200)


class ResponseTodoList(BaseModel):
    """TODOリストのレスポンススキーマ."""

    id: int
    title: str = Field(title="Todo List Title", min_length=1, max_length=100)
    description: str | None = Field(default=None, title="Todo List Description", min_length=1, max_length=200)
    created_at: datetime = Field(title="datetime that the item was created")
    updated_at: datetime = Field(title="datetime that the item was updated")


@app.get("/echo", tags=["Hello"])
def get_echo(message: str, name: str):
    Message = f"{message} {name}!"
    return {"Message": Message}

@app.get("/health", tags=["System"])
def get_health():
    status = "ok"
    return {"status": status}

@app.get("/lists/{todo_list_id}", tags=["Todoリスト"])
def get_todo_list(todo_list_id: int, session: Session = Depends(get_db)):
    db_list = session.query(ListModel).filter(ListModel.id == todo_list_id).first()
    
    return {
        "id": db_list.id,
        "title": db_list.title,
        "description": db_list.description,
        "created_at": db_list.created_at.isoformat(),
        "updated_at": db_list.updated_at.isoformat()
    }

@app.post("/lists", tags=["Todoリスト"])
def post_todo_list(new_todo: NewTodoList, session: Session = Depends(get_db)):
    db_list = ListModel(
        title=new_todo.title,
        description=new_todo.description,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
     # DBに保存
    session.add(db_list)
    session.commit()
    session.refresh(db_list)
    return {
        "id": db_list.id,
        "title": db_list.title,
        "description": db_list.description,
        "created_at": db_list.created_at.isoformat(),
        "updated_at": db_list.updated_at.isoformat()
    }

@app.put("/lists/{todo_list_id}", tags=["Todoリスト"])
def put_todo_list(todo_list_id: int, update_todo: UpdateTodoList, session: Session = Depends(get_db)):
    db_list = session.query(ListModel).filter(ListModel.id == todo_list_id).first()
    if update_todo.title is not None:
        db_list.title = update_todo.title
    if update_todo.description is not None:
        db_list.description = update_todo.description  
    # 更新日時を現在の時間に変更
    db_list.updated_at = datetime.utcnow()
    # DBに保存
    session.commit()
    session.refresh(db_list)

    return {
        "id": db_list.id,
        "title": db_list.title,
        "description": db_list.description,
        "created_at": db_list.created_at.isoformat(),
        "updated_at": db_list.updated_at.isoformat()
    }

@app.delete("/lists/{todo_list_id}", tags=["Todoリスト"])
def delete_todo_list(todo_list_id: int, session: Session = Depends(get_db)):
    db_list = session.query(ListModel).filter(ListModel.id == todo_list_id).first()
    session.delete(db_list)
    session.commit()
    return {}

@app.get("/lists/{todo_list_id}/items/{todo_item_id}", tags=["Todo項目"])
def get_todo_item(todo_list_id: int, todo_item_id: int, session: Session = Depends(get_db)):
    db_item = session.query(ItemModel).filter(
        ItemModel.id == todo_item_id, 
        ItemModel.todo_list_id == todo_list_id
    ).first()
    return {
        "id": db_item.id,
        "todo_list_id": db_item.todo_list_id,
        "title": db_item.title,
        "description": db_item.description,
        "status_code": db_item.status_code,
        "due_at": db_item.due_at.isoformat() if db_item.due_at else None,
        "created_at": db_item.created_at.isoformat(),
        "updated_at": db_item.updated_at.isoformat(),
    }

@app.post("/lists/{todo_list_id}/items", tags=["Todo項目"])
def post_todo_item(todo_list_id: int, new_todo: NewTodoItem, session: Session = Depends(get_db)):
    db_item = ItemModel(
        todo_list_id=todo_list_id,
        title=new_todo.title,
        description=new_todo.description,
        status_code=TodoItemStatusCode.NOT_COMPLETED.value,
        due_at=new_todo.due_at,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return {
        "id": db_item.id,
        "todo_list_id": db_item.todo_list_id,
        "title": db_item.title,
        "description": db_item.description,
        "status_code": db_item.status_code,
        "due_at": db_item.due_at.isoformat() if db_item.due_at else None,
        "created_at": db_item.created_at.isoformat(),
        "updated_at": db_item.updated_at.isoformat(),
    }

@app.put("/lists/{todo_list_id}/items/{todo_item_id}", tags=["Todo項目"])
def put_todo_item(todo_item_id: int, todo_list_id: int, update_todo_item: UpdateTodoItem, session: Session = Depends(get_db)):
    db_item = session.query(ItemModel).filter(
        ItemModel.id == todo_item_id, 
        ItemModel.todo_list_id == todo_list_id
    ).first()
    if update_todo_item.title is not None:
        db_item.title = update_todo_item.title
    if update_todo_item.description is not None:
        db_item.description = update_todo_item.description  
    if update_todo_item.due_at is not None:
        db_item.due_at = update_todo_item.due_at
    if update_todo_item.complete is not None:
        db_item.status_code = TodoItemStatusCode.COMPLETED.value if update_todo_item.complete else TodoItemStatusCode.NOT_COMPLETED.value
    
    db_item.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(db_item)
    return {
        "id": db_item.id,
        "todo_list_id": db_item.todo_list_id,
        "title": db_item.title,
        "description": db_item.description,
        "status_code": db_item.status_code,
        "due_at": db_item.due_at.isoformat() if db_item.due_at else None,
        "created_at": db_item.created_at.isoformat(),
        "updated_at": db_item.updated_at.isoformat(),
    }

@app.delete("/lists/{todo_list_id}/items/{todo_item_id}", tags=["Todoリスト"])
def delete_todo_list(todo_list_id: int, todo_item_id: int, session: Session = Depends(get_db)):
    db_item = session.query(ItemModel).filter(
        ItemModel.id == todo_item_id, 
        ItemModel.todo_list_id == todo_list_id
    ).first()
    session.delete(db_item)
    session.commit()
    return {}