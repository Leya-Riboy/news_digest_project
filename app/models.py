# app/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database import Base
from datetime import datetime, timezone

class ArticleModel(Base):
    __tablename__ = "articles"

    # Define columns (fields) for our table
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    source = Column(String, nullable=False)  # e.g., "Web Extract"
    url = Column(String, unique=True, nullable=False)  # Prevents scraping the same link twice
    raw_content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)     # Filled by Llama 3 later
    category = Column(String, nullable=True)   # Filled by Llama 3 later
    
    # Timezone-aware timestamp using a lambda callable
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))