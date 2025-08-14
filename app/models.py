from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float
from sqlalchemy.orm import relationship
from .database import Base

class Department(Base):
    __tablename__ = "Отделы"
    
    id = Column(Integer, primary_key=True, index=True)
    Название = Column(String(100), unique=True, index=True)
    
    Сотрудники = relationship("Employee", back_populates="Отдел")

class Position(Base):
    __tablename__ = "Должности"
    
    id = Column(Integer, primary_key=True, index=True)
    Название = Column(String(100), unique=True, index=True)
    
    Сотрудники = relationship("Employee", back_populates="Должность")

class Employee(Base):
    __tablename__ = "Сотрудники"
    
    id = Column(Integer, primary_key=True, index=True)
    ФИО = Column(String(100), index=True)
    ДР = Column(Date)
    Дата_Начала = Column(Date)
    ЗП = Column(Float)
    Ставка = Column(Float)
    Статус = Column(String(20))
    Номер_телефона = Column(String(20))
    email = Column(String(100))
    
    ID_Отдела = Column(Integer, ForeignKey("Отделы.id"))
    ID_Должности = Column(Integer, ForeignKey("Должности.id"))
    
    Отдел = relationship("Department", back_populates="Сотрудники")
    Должность = relationship("Position", back_populates="Сотрудники")