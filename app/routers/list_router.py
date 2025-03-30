from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.list_schema import NewTodoList, UpdateTodoList, ResponseTodoList
from app.crud.list_crud import get_todo_list, post_todo_list, put_todo_list, delete_todo_list, get_lists
from fastapi import HTTPException


router = APIRouter(
    prefix="/lists",
    tags=["Todoリスト"],
)

@router.get("/{todo_list_id}", tags=["Todoリスト"])
def get_list(todo_list_id: int, session: Session = Depends(get_db)):
    db_list = get_todo_list(todo_list_id, session)  # get_todo_list を使用
    if db_list is None:
        raise HTTPException(status_code=404, detail="Todo list not found")
    return get_todo_list(session, todo_list_id)

@router.post("/", tags=["Todoリスト"])
def post_list(new_todo: NewTodoList, session: Session = Depends(get_db)):
    return post_todo_list(new_todo, session)

@router.put("/{todo_list_id}", tags=["Todoリスト"])
def put_list(todo_list_id: int, update_todo: UpdateTodoList, session: Session = Depends(get_db)):
    return put_todo_list(todo_list_id, update_todo, session)

@router.delete("/{todo_list_id}", tags=["Todoリスト"])
def delete_list(todo_list_id: int, session: Session = Depends(get_db)):
    return delete_todo_list(todo_list_id, session)

@router.get("/", response_model=list[ResponseTodoList], tags=["Todoリスト"])
def get_todo_lists(page: int = 1, per_page: int = 10, session: Session = Depends(get_db) ):
    return get_lists(session, page, per_page)