from fastapi import Depends, FastAPI
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Ticket as TicketModel

app = FastAPI()


class Ticket(BaseModel):
    subject: str
    body: str


class TicketResponse(Ticket):
    id: int

    model_config = ConfigDict(from_attributes=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"message": "hello world"}


@app.post("/tickets", response_model=TicketResponse)
def create_ticket(ticket: Ticket, db: Session = Depends(get_db)):
    db_ticket = TicketModel(subject=ticket.subject, body=ticket.body)
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


@app.get("/tickets", response_model=list[TicketResponse])
def list_tickets(db: Session = Depends(get_db)):
    return db.query(TicketModel).all()
