from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from . import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    weekly_shifts = Column(Integer)

    shift_requests = relationship("ShiftRequest", back_populates="employee")
    shifts = relationship("Shift", back_populates="employee")