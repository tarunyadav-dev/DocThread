from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import List

# 1. THE SCHEMA: This dictates exactly what data every scraper MUST return.
class ScrapedDocument(BaseModel):
    url: str
    title: str
    framework: str
    markdown_content: str

# 2. THE BLUEPRINT: Any new scraper we build must inherit from this class.
class BaseScraperConnector(ABC):
    
    def __init__(self, framework_name: str, start_urls: List[str]):
        """
        Initialize the scraper with the framework name and the URLs to scrape.
        """
        self.framework_name = framework_name
        self.start_urls = start_urls

    @abstractmethod
    def scrape(self) -> List[ScrapedDocument]:
        """
        The core function. It must visit the URLs, extract the text, 
        and return a list of ScrapedDocument objects. 
        If a developer tries to build a scraper without this function, Python will throw an error.
        """
        pass