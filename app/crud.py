from sqlalchemy.orm import Session
from . import models, schemas
from datetime import date

def get_employee(db: Session, employee_id: int):
    return db.query(models.Employee).filter(models.Employee.id == employee_id).first()

def get_employees(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    ФИО: str = None,
    Мин_ЗП: float = None,
    Макс_ЗП: float = None,
    Дата_Начала: date = None,
    Дата_Окончания: date = None, 
    ID_Отдела: int = None
):
    query = db.query(models.Employee)
    
    if ФИО:
        query = query.filter(models.Employee.ФИО.ilike(f"%{ФИО}%"))
    if Мин_ЗП:
        query = query.filter(models.Employee.ЗП >= Мин_ЗП)
    if Макс_ЗП:
        query = query.filter(models.Employee.ЗП <= Макс_ЗП)
    if Дата_Начала:
        query = query.filter(models.Employee.Дата_Начала >= Дата_Начала)
    if Дата_Окончания:
        query = query.filter(models.Employee.Дата_Начала <= Дата_Окончания)
    if ID_Отдела:
        query = query.filter(models.Employee.ID_Отдела == ID_Отдела)
    
    return query.offset(skip).limit(limit).all()

def create_employee(db: Session, employee: schemas.EmployeeCreate):
    db_employee = models.Employee(
        ФИО=employee.ФИО,
        ДР=employee.Дата_ДР,
        Дата_Начала=employee.Дата_Начала,
        ЗП=employee.ЗП,
        Ставка=employee.Ставка,
        Статус=employee.Статус,
        Номер_телефона=employee.Номер_телефона,
        email=employee.email,
        ID_Отдела=employee.ID_Отдела,
        ID_Должности=employee.ID_Должности
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

def update_employee(db: Session, employee_id: int, employee_data: schemas.EmployeeUpdate):
    db_employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if db_employee:
        update_data = employee_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_employee, key, value)
        db.commit()
        db.refresh(db_employee)
    return db_employee

def delete_employee(db: Session, employee_id: int):
    db_employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if db_employee:
        db.delete(db_employee)
        db.commit()
        return True
    return False


def get_departments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Department).offset(skip).limit(limit).all()

def create_department(db: Session, department: schemas.DepartmentCreate):
    db_department = models.Department(**department.dict())
    db.add(db_department)
    db.commit()
    db.refresh(db_department)
    return db_department

def get_positions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Position).offset(skip).limit(limit).all()

def create_position(db: Session, position: schemas.PositionCreate):
    db_position = models.Position(**position.dict())
    db.add(db_position)
    db.commit()
    db.refresh(db_position)
    return db_position
