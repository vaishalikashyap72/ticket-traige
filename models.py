from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.sql import func

from database import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True)
    subject = Column(String)
    body = Column(String)


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)


class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(String)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    embedding = Column(Vector(1536), nullable=True)


class Resolution(Base):
    __tablename__ = "resolutions"

    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"))
    draft_response = Column(String)
    confidence_score = Column(Float, nullable=True)
    decision = Column(String)
    human_action = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
