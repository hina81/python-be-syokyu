from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.item_schema import NewTodoItem, UpdateTodoItem, ResponseTodoItem
from app.crud.item_crud import get_todo_item, post_todo_item, put_todo_item, delete_todo_list, get_items

router = APIRouter(
    prefix="/lists/{todo_list_id}/items",
    tags=["Todo項目"],
)

@router.get("/{todo_item_id}", tags=["Todo項目"])
def get_item(todo_list_id: int, todo_item_id: int, db: Session = Depends(get_db)):
    return get_todo_item(db, todo_item_id, todo_list_id)

@router.post("/", tags=["Todo項目"])
def post_item(todo_list_id: int, new_item: NewTodoItem, db: Session = Depends(get_db)):
    return post_todo_item(db, todo_list_id, new_item)

@router.put("/{todo_item_id}", tags=["Todo項目"])
def put_item(todo_item_id: int, todo_list_id: int, update_todo_item: UpdateTodoItem, db: Session = Depends(get_db)):
    return put_todo_item(db, todo_item_id, todo_list_id, update_todo_item)

@router.delete("/{todo_item_id}", tags=["Todo項目"])
def delete_list(todo_list_id: int, todo_item_id: int, db: Session = Depends(get_db)):
    delete_todo_list(db, todo_item_id, todo_list_id)
    return {}


@router.get("/", response_model=list[ResponseTodoItem], tags=["Todo項目"])
def get_todo_items(session: Session = Depends(get_db)):
    return get_items(session)