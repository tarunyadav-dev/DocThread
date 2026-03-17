import requests
import time
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup, Tag, NavigableString
from typing import List
from ingestion_engine.connectors.base_connector import BaseScraperConnector, ScrapedDocument

class FastapiScraper(BaseScraperConnector):
    def __init__(self):
        super().__init__(
            framework_name="FastAPI", 
            start_urls=["https://fastapi.tiangolo.com/"]
        )
        self.base_domain = "https://fastapi.tiangolo.com/"

    def is_english_doc(self, url: str) -> bool:
        """Filters out the massive amount of translated MkDocs pages (e.g., /es/, /ja/, /zh/)."""
        if not url.startswith(self.base_domain):
            return False
            
        # Get the path part of the URL
        path = url.replace(self.base_domain, "")
        
        # If the first segment is exactly 2 letters (like 'es', 'zh', 'pt'), it's a translation. Block it.
        if re.match(r'^[a-z]{2}/', path):
            return False
            
        # Block release notes and redundant index pages
        if path.startswith("release-notes"):
            return False
            
        return True

    def discover_links(self) -> List[str]:
        """Deep Crawler (BFS) optimized for MkDocs static site architecture."""
        print("🔍 Deploying Deep-Crawler for FastAPI Documentation...")
        
        visited = set([self.start_urls[0]])
        queue = [self.start_urls[0]]
        all_links = []

        while queue:
            current_url = queue.pop(0)
            
            if current_url != self.start_urls[0]:
                all_links.append(current_url)
                
            try:
                res = requests.get(current_url, timeout=10)
                soup = BeautifulSoup(res.text, 'html.parser')
                
                # MkDocs Material puts its navigation in <nav class="md-nav">
                nav = soup.find('nav', class_='md-nav')
                if not nav:
                    nav = soup # Fallback to whole page if nav is missing
                    
                for a in nav.find_all('a', href=True):
                    href = a['href']
                    full_url = urljoin(current_url, href)
                    clean_url = full_url.split('#')[0] # Drop anchor tags
                    
                    if self.is_english_doc(clean_url) and clean_url not in visited:
                        visited.add(clean_url)
                        queue.append(clean_url)
                        
            except Exception as e:
                print(f"⚠️ Link discovery error on {current_url}: {e}")
                
        print(f"🕸️ Spider complete! Found {len(all_links)} English FastAPI pages.")
        return all_links

    def smarter_markdown(self, element) -> str:
        """Recursive converter optimized for MkDocs Material features."""
        md = ""
        for child in element.children:
            if isinstance(child, NavigableString):
                text = str(child).strip()
                if text:
                    md += f" {text} "
            elif isinstance(child, Tag):
                # Headers
                if child.name in ['h1', 'h2', 'h3', 'h4']:
                    level = int(child.name[1])
                    md += f"\n\n{'#' * level} {child.get_text(strip=True)}\n\n"
                    
                # MkDocs Admonitions (Info, Warning, Tip boxes)
                elif child.name == 'div' and 'admonition' in child.get('class', []):
                    title_tag = child.find('p', class_='admonition-title')
                    title = title_tag.get_text(strip=True) if title_tag else "Note"
                    md += f"\n\n> **{title}:** "
                    # Get the rest of the text inside the admonition
                    content = child.get_text(separator=' ', strip=True).replace(title, '', 1)
                    md += f"{content}\n\n"
                    
                # Code Blocks (MkDocs uses <div class="highlight"><pre><code>)
                elif child.name == 'div' and 'highlight' in child.get('class', []):
                    code = child.get_text()
                    # Default to python since it's FastAPI
                    md += f"\n\n```python\n{code.strip()}\n```\n\n"
                    
                # Paragraphs
                elif child.name == 'p':
                    # Don't duplicate admonition titles
                    if 'admonition-title' not in child.get('class', []):
                        md += f"\n\n{child.get_text(separator=' ', strip=True)}\n\n"
                        
                # Inline Code
                elif child.name == 'code' and child.parent.name != 'pre':
                    md += f" `{child.get_text(strip=True)}` "
                    
                # Lists
                elif child.name == 'li':
                    md += f"\n* {child.get_text(strip=True)}"
                    
                # Recurse for standard divs
                else:
                    md += self.smarter_markdown(child)
        return md

    def scrape(self) -> List[ScrapedDocument]:
        all_urls = self.discover_links()
        documents = []

        for i, url in enumerate(all_urls):
            print(f"📄 [{i+1}/{len(all_urls)}] Scraping FastAPI: {url}")
            try:
                res = requests.get(url, timeout=10)
                soup = BeautifulSoup(res.text, 'html.parser')
                
                # MkDocs Material always uses <article class="md-content__inner md-typeset">
                article = soup.find('article', class_='md-content__inner')
                if not article:
                    continue

                # Clean up anchor links (the little paragraph symbols next to headers)
                for headerlink in article.find_all('a', class_='headerlink'):
                    headerlink.decompose()

                markdown_body = self.smarter_markdown(article)
                
                h1 = soup.find('h1')
                title = h1.get_text(strip=True) if h1 else f"FastAPI Page {i}"

                documents.append(ScrapedDocument(
                    url=url,
                    title=title,
                    framework=self.framework_name,
                    markdown_content=markdown_body
                ))
                
                time.sleep(0.5) # Polite delay
            except Exception as e:
                print(f"⚠️ Error on {url}: {e}")

        return documents