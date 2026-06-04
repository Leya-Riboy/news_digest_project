# app/services/scraper.py
import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod

# 1. Base Class (Abstraction)
class BaseScraper(ABC):
    @abstractmethod
    def scrape(self, url: str) -> dict:
        pass

# 2. Concrete Adapter for Site A (e.g., a simple blog or news site)
class GenericBlogScraper(BaseScraper):
    def scrape(self, url: str) -> dict:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")
        
        # entry-level target: get title and all paragraph text
        title = soup.find("h1").get_text(strip=True) if soup.find("h1") else "No Title"
        
        paragraphs = soup.find_all("p")
        content = " ".join([p.get_text(strip=True) for p in paragraphs[:5]]) # Take first 5 paragraphs
        
        return {
            "title": title,
            "url": url,
            "raw_content": content
        }