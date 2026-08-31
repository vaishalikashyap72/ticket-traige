from datetime import datetime

from fastapi import Depends, FastAPI
from pydantic import BaseModel, ConfigDict
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import Base, SessionLocal, engine
from models import Category as CategoryModel
from models import KnowledgeBase as KnowledgeBaseModel
from models import Resolution as ResolutionModel
from models import Ticket as TicketModel

app = FastAPI()


@app.on_event("startup")
def create_tables():
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    Base.metadata.create_all(bind=engine)


class Ticket(BaseModel):
    subject: str
    body: str


class TicketResponse(Ticket):
    id: int

    model_config = ConfigDict(from_attributes=True)


class Category(BaseModel):
    name: str
    description: str


class CategoryResponse(Category):
    id: int

    model_config = ConfigDict(from_attributes=True)


class KnowledgeBase(BaseModel):
    title: str
    content: str
    category_id: int | None = None


class KnowledgeBaseResponse(KnowledgeBase):
    id: int
    embedding: list[float] | None = None

    model_config = ConfigDict(from_attributes=True)


class Resolution(BaseModel):
    ticket_id: int
    draft_response: str
    confidence_score: float | None = None
    decision: str
    human_action: str | None = None


class ResolutionResponse(Resolution):
    id: int
    created_at: datetime

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


@app.get("/tickets/{ticket_id}/resolutions", response_model=list[ResolutionResponse])
def list_ticket_resolutions(ticket_id: int, db: Session = Depends(get_db)):
    return (
        db.query(ResolutionModel)
        .filter(ResolutionModel.ticket_id == ticket_id)
        .all()
    )


@app.post("/categories", response_model=CategoryResponse)
def create_category(category: Category, db: Session = Depends(get_db)):
    db_category = CategoryModel(name=category.name, description=category.description)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@app.get("/categories", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return db.query(CategoryModel).all()


@app.post("/knowledge-base", response_model=KnowledgeBaseResponse)
def create_knowledge_base_entry(
    entry: KnowledgeBase, db: Session = Depends(get_db)
):
    db_entry = KnowledgeBaseModel(
        title=entry.title,
        content=entry.content,
        category_id=entry.category_id,
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


@app.get("/knowledge-base", response_model=list[KnowledgeBaseResponse])
def list_knowledge_base_entries(db: Session = Depends(get_db)):
    return db.query(KnowledgeBaseModel).all()


@app.post("/resolutions", response_model=ResolutionResponse)
def create_resolution(resolution: Resolution, db: Session = Depends(get_db)):
    db_resolution = ResolutionModel(
        ticket_id=resolution.ticket_id,
        draft_response=resolution.draft_response,
        confidence_score=resolution.confidence_score,
        decision=resolution.decision,
        human_action=resolution.human_action,
    )
    db.add(db_resolution)
    db.commit()
    db.refresh(db_resolution)
    return db_resolution


@app.get("/resolutions", response_model=list[ResolutionResponse])
def list_resolutions(db: Session = Depends(get_db)):
    return db.query(ResolutionModel).all()
