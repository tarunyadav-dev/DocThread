# Exposing these at the folder level so they are easy to import
from .base_connector import BaseScraperConnector, ScrapedDocument

__all__ = ["BaseScraperConnector", "ScrapedDocument"]