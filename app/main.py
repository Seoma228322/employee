from fastapi import FastAPI, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from datetime import date
from typing import Optional
import time

from . import models, crud, schemas
from .database import SessionLocal, engine

app = FastAPI(title="Система менеджмента сотрудников")

templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def on_startup():
    print("Ожидание подключения к базе данных...")
    while True:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("Подключение к базе данных установлено.")
            break
        except OperationalError as e:
            print("Ошибка подключения к БД: ", e)
            print("Ждём 2 секунды перед повторной попыткой...")
            time.sleep(2)

    print("Создаём таблицы в базе данных (если ещё не созданы)...")
    models.Base.metadata.create_all(bind=engine)
    print("Таблицы успешно созданы.")

@app.get("/employees/create", response_class=HTMLResponse)
async def create_employee_form(request: Request, db: Session = Depends(get_db)):
    departments = crud.get_departments(db)
    positions = crud.get_positions(db)
    return templates.TemplateResponse("employee_form.html", {
        "request": request,
        "employee": None, 
        "departments": departments,
        "positions": positions
    })

@app.get("/employees/{employee_id}", response_class=HTMLResponse) 
async def read_employee(request: Request, employee_id: 
                        int, db: Session = Depends(get_db)):
    employee = crud.get_employee(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    return templates.TemplateResponse("employee_detail.html", 
                                      {"request": request, "employee": employee})

@app.get("/", response_class=HTMLResponse)
async def read_employees(
    request: Request,
    skip: int = 0,
    limit: int = 10,
    ФИО: Optional[str] = None,
    Мин_ЗП: Optional[str] = None,
    Макс_ЗП: Optional[str] = None,
    Дата_Начала: Optional[str] = None,
    Дата_Окончания: Optional[str] = None,
    ID_Отдела: Optional[str] = None,
    db: Session = Depends(get_db)
):

    if Дата_Начала == "":
        Дата_Начала = None
    if Дата_Окончания == "":
        Дата_Окончания = None

    processed_Дата_Начала = None
    processed_Дата_Окончания = None

    if Дата_Начала:
        try:
            processed_Дата_Начала = date.fromisoformat(Дата_Начала)
        except ValueError:
            processed_Дата_Начала = None

    if Дата_Окончания:
        try:
            processed_Дата_Окончания = date.fromisoformat(Дата_Окончания)
        except ValueError:
            processed_Дата_Окончания = None

    if ID_Отдела == "":
        ID_Отдела = None

    processed_ID_Отдела = None
    if ID_Отдела:
        try:
            processed_ID_Отдела = int(ID_Отдела)
        except ValueError:
            processed_ID_Отдела = None

    if Мин_ЗП == "":
        Мин_ЗП = None
    if Макс_ЗП == "":
        Макс_ЗП = None

    processed_Мин_ЗП = None
    processed_Макс_ЗП = None

    if Мин_ЗП:
        try:
            processed_Мин_ЗП = float(Мин_ЗП)
        except ValueError:
            processed_Мин_ЗП = None

    if Макс_ЗП:
        try:
            processed_Макс_ЗП = float(Макс_ЗП)
        except ValueError:
            processed_Макс_ЗП = None

    employees = crud.get_employees(
        db,
        skip=skip,
        limit=limit,
        ФИО=ФИО,
        Мин_ЗП=processed_Мин_ЗП,
        Макс_ЗП=processed_Макс_ЗП,
        Дата_Начала=processed_Дата_Начала,
        Дата_Окончания=processed_Дата_Окончания,
        ID_Отдела=processed_ID_Отдела
    )
    departments = crud.get_departments(db)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "employees": employees,
        "departments": departments,
        "filters": {
            "ФИО": ФИО or "",
            "Мин_ЗП": Мин_ЗП or "",
            "Макс_ЗП": Макс_ЗП or "",
            "Дата_Начала": Дата_Начала or "",
            "Дата_Окончания": Дата_Окончания or "",
            "ID_Отдела": ID_Отдела or ""
        },
        "pagination": {
            "skip": skip,
            "limit": limit
        }
    })

@app.post("/employees/", response_class=RedirectResponse)
async def create_employee_action(
    request: Request,
    ФИО: str = Form(...),
    Дата_ДР: date = Form(...),
    Дата_Начала: date = Form(...),
    ЗП: float = Form(...),
    Ставка: float = Form(...),
    Статус: str = Form(...),
    Номер_телефона: str = Form(...),
    email: str = Form(...),
    ID_Отдела: int = Form(...),
    ID_Должности: int = Form(...),
    db: Session = Depends(get_db)
):
    employee_data = schemas.EmployeeCreate(
        ФИО=ФИО,
        Дата_ДР=Дата_ДР,
        Дата_Начала=Дата_Начала,
        ЗП=ЗП,
        Ставка=Ставка,
        Статус=Статус,
        Номер_телефона=Номер_телефона,
        email=email,
        ID_Отдела=ID_Отдела,
        ID_Должности=ID_Должности
    )
    crud.create_employee(db, employee_data)
    return RedirectResponse(url="/", status_code=303)


@app.get("/employees/{employee_id}/edit", response_class=HTMLResponse)
async def update_employee_form(request: Request, employee_id: int, db: Session = Depends(get_db)):
    employee = crud.get_employee(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    departments = crud.get_departments(db)
    positions = crud.get_positions(db)
    return templates.TemplateResponse("employee_form.html", {
        "request": request,
        "employee": employee,
        "departments": departments,
        "positions": positions
    })


@app.post("/employees/{employee_id}/update", response_class=RedirectResponse)
async def update_employee_action(
    request: Request,
    employee_id: int,
    ФИО: str = Form(...),
    Дата_ДР: date = Form(...),
    Дата_Начала: date = Form(...),
    ЗП: float = Form(...),
    Ставка: float = Form(...),
    Статус: str = Form(...),
    Номер_телефона: str = Form(...),
    email: str = Form(...),
    ID_Отдела: int = Form(...),
    ID_Должности: int = Form(...),
    db: Session = Depends(get_db)
):
    employee_data = {
        "ФИО": ФИО,
        "Дата_ДР": Дата_ДР,
        "Дата_Начала": Дата_Начала,
        "ЗП": ЗП,
        "Ставка": Ставка,
        "Статус": Статус,
        "Номер_телефона": Номер_телефона,
        "email": email,
        "ID_Отдела": ID_Отдела,
        "ID_Должности": ID_Должности
    }

    crud.update_employee(db, employee_id, employee_data)
    return RedirectResponse(url=f"/employees/{employee_id}", status_code=303)


@app.post("/employees/{employee_id}/delete", response_class=RedirectResponse)
async def delete_employee_action(request: Request, employee_id: int, db: Session = Depends(get_db)):
    crud.delete_employee(db, employee_id)
    return RedirectResponse(url="/", status_code=303)

@app.get("/departments/create", response_class=HTMLResponse)
async def create_department_form(request: Request):
    return templates.TemplateResponse("department_form.html", {"request": request})

@app.get("/departments/", response_class=HTMLResponse)
async def list_departments(request: Request, db: Session = Depends(get_db)):
    departments = crud.get_departments(db)
    return templates.TemplateResponse("departments_list.html", {"request": request, "departments": departments})


@app.post("/departments/", response_class=RedirectResponse)
async def create_department_action(
    request: Request,
    Название: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        department_data = schemas.DepartmentCreate(Название=Название)
        crud.create_department(db, department_data)
        return RedirectResponse(url="/departments/", status_code=303)
    except Exception as e:
        print(f"Ошибка при создании отдела: {e}")
        return templates.TemplateResponse("department_form.html", 
                                          {"request": request, "error": "Ошибка при создании отдела."}, 
                                          status_code=400)
    
@app.get("/positions/create", response_class=HTMLResponse)
async def create_position_form(request: Request):
    return templates.TemplateResponse("position_form.html", {"request": request})

@app.get("/positions/", response_class=HTMLResponse)
async def list_position(request: Request, db: Session = Depends(get_db)):
    positions = crud.get_positions(db)
    return templates.TemplateResponse("position_list.html", {"request": request, "positions": positions})

@app.post("/positions/", response_class=RedirectResponse)
async def create_position_action(
    request: Request,
    Название: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        position_data = schemas.PositionCreate(Название=Название)
        crud.create_position(db, position_data)
        return RedirectResponse(url = "/positions/", status_code=303)
    except Exception as e:
        print(f"Ошибка при создании должности: {e}")
        return templates.TemplateResponse("position_form.html",
                                          {"request": request, "error": "Ошибка при создании должности."},
                                          status_code=400)