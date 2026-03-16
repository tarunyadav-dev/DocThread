# 🔌 DocThread Scraper Connectors

This directory contains the individual web scrapers for each documentation source.

## How to build a new Scraper

To add a new framework (e.g., `FastAPI`), you must follow these exact rules so the `run_terminal.py` engine can understand it:

1. **Create a new file:** `fastapi_docs.py`
2. **Inherit from the Base:** Your class must inherit from `BaseScraperConnector`.
3. **Return the Schema:** Your `scrape()` function MUST return a list of `ScrapedDocument` objects. 

### Template:
```python
from typing import List
from .base_connector import BaseScraperConnector, ScrapedDocument

class FastAPIScraper(BaseScraperConnector):
    def __init__(self):
        super().__init__(framework_name="FastAPI", start_urls=["[https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)"])

    def scrape(self) -> List[ScrapedDocument]:
        documents = []
        
        # ... your beautifulsoup or crawl4ai logic here ...
        
        # You MUST return data in this exact shape:
        documents.append(ScrapedDocument(
            url="https://...",
            title="Introduction",
            framework=self.framework_name,
            markdown_content="# Introduction \n This is the text..."
        ))
        
        return documents