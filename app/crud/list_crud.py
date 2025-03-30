from datetime import datetime
from app.models.list_model import ListModel
from sqlalchemy.orm import Session
from app.schemas.list_schema import NewTodoList, UpdateTodoList, ResponseTodoList
from fastapi import HTTPException

def get_todo_list(todo_list_id: int, session: Session):
    return session.query(ListModel).filter(ListModel.id == todo_list_id).first()

def post_todo_list(new_todo: NewTodoList, session: Session ):
    db_list = ListModel(
        title=new_todo.title,
        description=new_todo.description,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    session.add(db_list)
    session.commit()
    session.refresh(db_list)
    return db_list

def put_todo_list(todo_list_id: int, update_todo: UpdateTodoList, session: Session):
    db_list = session.query(ListModel).filter(ListModel.id == todo_list_id).first()
    if db_list is None:
        raise HTTPException(status_code=404, detail="Todo list not found")

    if update_todo.title is not None:
        db_list.title = update_todo.title
    if update_todo.description is not None:
        db_list.description = update_todo.description  
    db_list.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(db_list)

    return db_list

def delete_todo_list(todo_list_id: int, session: Session):
    db_list = session.query(ListModel).filter(ListModel.id == todo_list_id).first()
    if db_list is None:
        raise HTTPException(status_code=404, detail="Todo list not found")
    
    session.delete(db_list)
    session.commit()
    return {}


def get_lists(session: Session) -> list[ResponseTodoList]:
    db_todo_lists = session.query(ListModel).all()
    return db_todo_lists