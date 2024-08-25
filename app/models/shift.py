from sqlalchemy import Column, Integer, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from . import Base

class ShiftRequest(Base):
    __tablename__ = "shift_requests"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    date = Column(Date)
    start_time = Column(Time)
    end_time = Column(Time)

    employee = relationship("Employee", back_populates="shift_requests")

class Shift(Base):
    __tablename__ = "shifts"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    date = Column(Date)
    start_time = Column(Time)
    end_time = Column(Time)
    
    employee = relationship("Employee", back_populates="shifts")