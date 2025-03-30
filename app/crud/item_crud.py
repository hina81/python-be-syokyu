from datetime import datetime
from app.models.item_model import ItemModel
from app.models.list_model import ListModel
from sqlalchemy.orm import Session
from app.schemas.item_schema import NewTodoItem, UpdateTodoItem, ResponseTodoItem
from app.const import TodoItemStatusCode
from fastapi import HTTPException

def get_todo_item(db:Session, todo_list_id: int, todo_item_id: int):
    db_item = db.query(ItemModel).filter(
        ItemModel.id == todo_item_id, 
        ItemModel.todo_list_id == todo_list_id
    ).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Todo item not found")
    return db_item

def post_todo_item(db: Session, todo_list_id: int, new_item: NewTodoItem):
    db_list = db.query(ListModel).filter(ListModel.id == todo_list_id).first()
    if db_list is None:
        raise HTTPException(status_code=404, detail="Todo list not found")

    db_item = ItemModel(
        todo_list_id=todo_list_id,
        title=new_item.title,
        description=new_item.description,
        status_code=TodoItemStatusCode.NOT_COMPLETED.value,
        due_at=new_item.due_at,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def put_todo_item(db:Session, todo_item_id: int, todo_list_id: int, update_todo_item: UpdateTodoItem):
    db_item = db.query(ItemModel).filter(
        ItemModel.id == todo_item_id, 
        ItemModel.todo_list_id == todo_list_id
    ).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Todo item not found")
    if update_todo_item.title is not None:
        db_item.title = update_todo_item.title
    if update_todo_item.description is not None:
        db_item.description = update_todo_item.description  
    if update_todo_item.due_at is not None:
        db_item.due_at = update_todo_item.due_at
    if update_todo_item.complete is not None:
        db_item.status_code = TodoItemStatusCode.COMPLETED.value if update_todo_item.complete else TodoItemStatusCode.NOT_COMPLETED.value
    
    db_item.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_todo_list(todo_list_id: int, todo_item_id: int, db: Session):
    db_item = db.query(ItemModel).filter(
        ItemModel.id == todo_item_id, 
        ItemModel.todo_list_id == todo_list_id
    ).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Todo item not found")
    db.delete(db_item)
    db.commit()
    return {}

def get_items(session: Session, todo_list_id: int, page: int = 1, per_page: int = 10) -> list[ResponseTodoItem]:
    offset = (page - 1) * per_page
    db_items = session.query(ItemModel).filter(ItemModel.todo_list_id == todo_list_id).offset(offset).limit(per_page).all()
    return db_items