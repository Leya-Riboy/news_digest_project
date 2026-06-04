# app/main.py
import os
from fastapi import FastAPI, Depends, HTTPException, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import datetime

from app.database import SessionLocal, engine, Base
from app.models import ArticleModel
from app.services.scraper import GenericBlogScraper
from app.services.llm import DigestLLMEngine
from app.utils.builder import DailyDigestBuilder

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Content Aggregator API & Frontend")

# Setup Jinja2 templates directory configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------------------------------------------------------
# 🖥️ FRONTEND WEB UI ROUTES
# ----------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def render_dashboard(request: Request, db: Session = Depends(get_db)):
    """Fetches all processed articles from the database and guarantees raw text fields."""
    raw_articles = db.query(ArticleModel).order_by(ArticleModel.created_at.desc()).all()
    
    sanitized_articles = []
    for art in raw_articles:
        # Intercept any implicit SQLAlchemy dictionary type mapping structures
        if isinstance(art.category, dict):
            art.category = art.category.get("category", "General")
        else:
            art.category = str(art.category) if art.category else "General"
            
        if isinstance(art.summary, dict):
            art.summary = art.summary.get("summary", "No summary available.")
        else:
            art.summary = str(art.summary) if art.summary else "No summary available."
            
        sanitized_articles.append(art)
    
    # Injects the validated records into index.html via Jinja2 contexts
    return templates.TemplateResponse(
        request=request,
        name="index.html", 
        context={"articles": raw_articles}
    )

@app.post("/fetch-web")
def handle_frontend_form_submit(url: str = Form(...), db: Session = Depends(get_db)):
    existing = db.query(ArticleModel).filter(ArticleModel.url == url).first()
    if existing:
        return RedirectResponse(url="/", status_code=303)

    scraper = GenericBlogScraper()
    try:
        raw_data = scraper.scrape(url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to scrape site: {str(e)}")

    llm = DigestLLMEngine()
    llm_output = llm.generate_summary(raw_data["raw_content"])

    # 🛠️ SAFE EXTRACT: Check if the LLM output is a dictionary or a tuple
    if isinstance(llm_output, dict):
        clean_summary = llm_output.get("summary", "No summary generated.")
        clean_category = llm_output.get("category", "General")
    elif isinstance(llm_output, (list, tuple)) and len(llm_output) >= 2:
        clean_summary, clean_category = llm_output
    else:
        clean_summary = str(llm_output)
        clean_category = "General"

    # Force conversion to strings just to be bulletproof
    clean_summary = str(clean_summary.get("summary", clean_summary)) if isinstance(clean_summary, dict) else str(clean_summary)
    clean_category = str(clean_category.get("category", clean_category)) if isinstance(clean_category, dict) else str(clean_category)

    new_article = ArticleModel(
        title=raw_data["title"],
        source="Web Extract",
        url=url,
        raw_content=raw_data["raw_content"],
        summary=clean_summary,
        category=clean_category
    )
    db.add(new_article)
    db.commit()

    return RedirectResponse(url="/", status_code=303)

# ----------------------------------------------------------------
# 🔌 ORIGINAL REST API ENDPOINTS (Maintained for backward compatibility)
# ----------------------------------------------------------------

@app.post("/api/v1/fetch")
def fetch_and_process_article(url: str, db: Session = Depends(get_db)):
    existing = db.query(ArticleModel).filter(ArticleModel.url == url).first()
    if existing:
        return {"message": "Article already processed", "article_id": existing.id}

    scraper = GenericBlogScraper()
    try:
        raw_data = scraper.scrape(url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to scrape site: {str(e)}")

    llm = DigestLLMEngine()
    llm_output = llm.generate_summary(raw_data["raw_content"])

    # 🛠️ SAFE EXTRACT: Check if the LLM output is a dictionary or a tuple
    if isinstance(llm_output, dict):
        clean_summary = llm_output.get("summary", "No summary generated.")
        clean_category = llm_output.get("category", "General")
    elif isinstance(llm_output, (list, tuple)) and len(llm_output) >= 2:
        clean_summary, clean_category = llm_output
    else:
        clean_summary = str(llm_output)
        clean_category = "General"

    # Force final validation to text strings
    clean_summary = str(clean_summary.get("summary", clean_summary)) if isinstance(clean_summary, dict) else str(clean_summary)
    clean_category = str(clean_category.get("category", clean_category)) if isinstance(clean_category, dict) else str(clean_category)

    new_article = ArticleModel(
        title=raw_data["title"],
        source="Web Extract",
        url=url,
        raw_content=raw_data["raw_content"],
        summary=clean_summary,
        category=clean_category
    )
    db.add(new_article)
    db.commit()
    db.refresh(new_article)

    return {"status": "success", "category": clean_category, "summary": clean_summary}

@app.get("/api/v1/digest")
def get_daily_digest(db: Session = Depends(get_db)):
    # Fetch all articles added today
    today = datetime.date.today()
    articles = db.query(ArticleModel).filter(ArticleModel.created_at >= today).all()

    if not articles:
        return {"message": "No articles processed today yet. Use the /fetch endpoint first!"}

    # Group articles by category for the builder safely
    grouped = {}
    for art in articles:
        # 🛠️ SAFE CHECK: Extract text key if category is accidentally stored as a dict
        if isinstance(art.category, dict):
            category_key = art.category.get("category", "General")
        elif isinstance(art.category, str):
            category_key = art.category
        else:
            category_key = "General"

        grouped.setdefault(category_key, []).append(art)

    # Use our OOP Builder Pattern to make the newsletter string
    builder = DailyDigestBuilder()
    builder.add_header(today.strftime("%Y-%m-%d"))
    
    for category, arts in grouped.items():
        builder.add_section(category, arts)
        
    builder.add_footer()
    
    # Return raw text formatting cleanly
    return {"digest": builder.build()}