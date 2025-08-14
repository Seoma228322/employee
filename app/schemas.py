from datetime import date
from typing import Optional
from pydantic import BaseModel


class EmployeeBase(BaseModel):
    ФИО: str
    Дата_ДР: date
    Дата_Начала: date
    ЗП: float
    Ставка: float
    Статус: str
    Номер_телефона: str
    email: str
    ID_Отдела: int
    ID_Должности: int

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    ФИО: Optional[str] = None
    Дата_ДР: Optional[date] = None
    Дата_Начала: Optional[date] = None
    ЗП: Optional[float] = None
    Ставка: Optional[float] = None
    Статус: Optional[str] = None
    Номер_телефона: Optional[str] = None
    email: Optional[str] = None
    ID_Отдела: Optional[int] = None
    ID_Должности: Optional[int] = None

class Employee(EmployeeBase):
    id: int

    class Config:
        from_attributes = True

class DepartmentBase(BaseModel):
    Название: str

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(DepartmentBase):
    pass

class Department(DepartmentBase):
    id: int

    class Config:
        from_attributes = True


class PositionBase(BaseModel):
    Название: str

class PositionCreate(PositionBase):
    pass

class PositionUpdate(PositionBase):
    pass

class Position(PositionBase):
    id: int

    class Config:
        from_attributes = True
