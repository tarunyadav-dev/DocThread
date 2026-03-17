import requests
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup, Tag, NavigableString
from typing import List
from ingestion_engine.connectors.base_connector import BaseScraperConnector, ScrapedDocument

class PythonScraper(BaseScraperConnector):
    def __init__(self):
        super().__init__(
            framework_name="Python", 
            start_urls=["https://docs.python.org/3/"]
        )
        # Lock the spider to Python 3 English docs only
        self.base_path = "https://docs.python.org/3/"
        
        # Blacklist useless pages that break RAG or cause infinite loops
        self.blacklist = [
            '/genindex.html', 
            '/py-modindex.html', 
            '/search.html', 
            '_sources/', 
            '/bugs.html',
            '/about.html',
            '/license.html'
        ]

    def is_valid_link(self, url: str) -> bool:
        """Checks if the URL is valid, inside the base path, and not blacklisted."""
        if not url.startswith(self.base_path):
            return False
        if not url.endswith('.html'):
            return False
        for bad_path in self.blacklist:
            if bad_path in url:
                return False
        return True

    def discover_links(self) -> List[str]:
        """Deep Crawler (BFS) mapped for the massive Python Documentation."""
        print("🔍 Deploying Deep-Crawler for Python 3 Documentation...")
        print("⚠️  WARNING: The Python docs are massive (~1000+ pages). This discovery phase will take a moment.")
        
        visited = set([self.start_urls[0]])
        queue = [self.start_urls[0]]
        all_links = []

        while queue:
            current_url = queue.pop(0)
            
            # Add to scraping list (except the root index which is just a TOC)
            if current_url != self.start_urls[0]:
                all_links.append(current_url)
                
            try:
                res = requests.get(current_url, timeout=10)
                soup = BeautifulSoup(res.text, 'html.parser')
                
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    full_url = urljoin(current_url, href)
                    clean_url = full_url.split('#')[0] # Drop anchor tags
                    
                    if self.is_valid_link(clean_url) and clean_url not in visited:
                        visited.add(clean_url)
                        queue.append(clean_url)
                        
            except Exception as e:
                print(f"⚠️ Link discovery error on {current_url}: {e}")
                
        print(f"🕸️ Spider complete! Found {len(all_links)} Python pages.")
        return all_links

    def smarter_markdown(self, element) -> str:
        """Recursive converter optimized for Sphinx HTML structures."""
        md = ""
        for child in element.children:
            if isinstance(child, NavigableString):
                text = str(child).strip()
                if text:
                    md += f" {text} "
            elif isinstance(child, Tag):
                if child.name in ['h1', 'h2', 'h3', 'h4', 'h5']:
                    level = int(child.name[1])
                    md += f"\n\n{'#' * level} {child.get_text(strip=True)}\n\n"
                elif child.name == 'p':
                    md += f"\n\n{child.get_text(separator=' ', strip=True)}\n\n"
                elif child.name in ['pre', 'div'] and ('highlight' in child.get('class', []) or child.name == 'pre'):
                    code = child.get_text()
                    md += f"\n\n```python\n{code.strip()}\n```\n\n"
                elif child.name in ['code', 'span'] and ('pre' in child.get('class', []) or child.name == 'code'):
                    md += f" `{child.get_text(strip=True)}` "
                elif child.name == 'li':
                    md += f"\n* {child.get_text(strip=True)}"
                elif child.name in ['div', 'section']:
                    # Special handling for Python's warning/note boxes
                    if 'admonition' in child.get('class', []):
                        title = child.find('p', class_='admonition-title')
                        title_text = title.get_text(strip=True) if title else "Note"
                        md += f"\n\n> **{title_text}:** "
                    md += self.smarter_markdown(child)
                else:
                    md += self.smarter_markdown(child)
        return md

    def scrape(self) -> List[ScrapedDocument]:
        all_urls = self.discover_links()
        documents = []

        for i, url in enumerate(all_urls):
            print(f"📄 [{i+1}/{len(all_urls)}] Scraping Python: {url}")
            try:
                res = requests.get(url, timeout=10)
                soup = BeautifulSoup(res.text, 'html.parser')
                
                # Python docs usually keep main content in a div with role="main" or class="body"
                article = soup.find('div', role='main') or soup.find('div', class_='body')
                if not article:
                    continue

                # Cleanup junk (navigation bars, sidebars, internal anchor links)
                for junk in article(['script', 'style', 'nav', 'a.headerlink', 'div.sphinxsidebar']):
                    junk.decompose()

                markdown_body = self.smarter_markdown(article)
                
                h1 = soup.find('h1')
                title = h1.get_text(strip=True) if h1 else f"Python Page {i}"

                documents.append(ScrapedDocument(
                    url=url,
                    title=title,
                    framework=self.framework_name,
                    markdown_content=markdown_body
                ))
                
                time.sleep(0.5) # Polite delay is critical here so Python.org doesn't ban us
            except Exception as e:
                print(f"⚠️ Error on {url}: {e}")

        return documents