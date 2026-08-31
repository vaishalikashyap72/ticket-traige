from sqlalchemy import Column, Integer, String

from database import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True)
    subject = Column(String)
    body = Column(String)
