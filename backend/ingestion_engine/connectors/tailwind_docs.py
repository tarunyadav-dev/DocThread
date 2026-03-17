from typing import List
from ingestion_engine.connectors.base_connector import BaseScraperConnector, ScrapedDocument

class TailwindScraper(BaseScraperConnector):
    def __init__(self):
        super().__init__(
            framework_name="Tailwind CSS", 
            start_urls=["https://example.com/docs"]
        )

    def scrape(self) -> List[ScrapedDocument]:
        print(f"👋 Hello! The {self.framework_name} scraper is currently a placeholder.")
        print("🛠️  Ready to be coded when you are!")
        return []
