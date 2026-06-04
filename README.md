# 🤖 AI Content Aggregator & Daily Digest Pipeline

A production-grade, full-stack AI Content Aggregator that scrapes user-submitted blog URLs, extracts their main reading layout, processes the content using **Llama 3 (via Groq Cloud)**, organizes the articles by topic, and builds a clean daily email/newsletter digest.

## 🚀 Live Demo & Dashboard
* **Live Application:** [https://news-digest-project.onrender.com]
* **Interactive API Documentation:** `https://news-digest-project.onrender.com/docs`

---

## 🛠️ Tech Stack & Architecture

* **Framework:** FastAPI (Python 3.10+)
* **Frontend UI:** HTML5, Jinja2 Templates, Tailwind CSS v4 (via CDN)
* **Database & ORM:** SQLite, SQLAlchemy
* **AI Engine:** Groq Cloud SDK (`llama3-8b-8192`)
* **Scraping Engine:** BeautifulSoup4 / Requests (Generic Scraper)
* **Design Pattern:** Object-Oriented Builder Pattern (Daily Digest Constructor)

---

## 🌟 Key Features

- **Automated Web Scraping:** Extracts clean content text and metadata dynamically from unstructured blog post URLs.
- **Llama 3 AI Text Processing:** Automatically processes raw text layout structures to generate human-grade abstractive summaries and topic category classifications.
- **Resilient Type Validation:** Built-in validation architecture handling nested JSON mutations and data types securely.
- **Dynamic Frontend Dashboard:** Beautiful dark-mode dashboard providing seamless layout rendering via modern Starlette template architectures.
- **OOP Newsletter Builder:** Custom daily aggregation design pattern that filters, categorizes, and formats your daily pipeline updates cleanly.

---

## ⚙️ Local Development Setup

Follow these simple steps to spin up the full application environment locally on your machine.

### 1. Clone the Project
```bash
git clone [https://github.com/Leya-Riboy/news-digest-project.git](https://github.com/Leya-Riboy/news-digest-project.git)
cd news-digest-project