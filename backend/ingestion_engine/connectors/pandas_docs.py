import requests
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup, Tag, NavigableString
from typing import List
from ingestion_engine.connectors.base_connector import BaseScraperConnector, ScrapedDocument

class PandasScraper(BaseScraperConnector):
    def __init__(self):
        # We start at the User Guide index
        super().__init__(
            framework_name="Pandas", 
            start_urls=["https://pandas.pydata.org/docs/user_guide/index.html"]
        )

    def discover_links(self) -> List[str]:
        """Finds all 29+ documentation links from the User Guide index."""
        print("🔍 Scanning User Guide Index for all pages...")
        try:
            res = requests.get(self.start_urls[0], timeout=15)
            soup = BeautifulSoup(res.text, 'html.parser')
            links = []
            
            # The sidebar or the main TOC list
            toc = soup.find('nav', class_='bd-links') or soup.find('div', class_='toctree-wrapper')
            
            if not toc:
                print("⚠️ Could not find TOC. Using fallback scan.")
                toc = soup.find('article')

            for a in toc.find_all('a', href=True):
                href = a['href']
                # Clean the URL: join relative paths to the base
                full_url = urljoin(self.start_urls[0], href)
                # Ensure we stay within the user_guide and ignore section anchors (#)
                clean_url = full_url.split('#')[0]
                
                if "user_guide" in clean_url and clean_url not in links and clean_url.endswith('.html'):
                    links.append(clean_url)
            
            # Remove the index page itself from the list to avoid infinite loop
            links = [l for l in links if not l.endswith('index.html')]
            
            print(f"🕸️ Found {len(links)} total pages to scrape.")
            return links
        except Exception as e:
            print(f"❌ Failed to index links: {e}")
            return []

    def smarter_markdown(self, element) -> str:
        """Recursive converter that preserves headers, code, and lists."""
        md = ""
        for child in element.children:
            if isinstance(child, NavigableString):
                text = str(child).strip()
                if text:
                    md += f" {text} "
            elif isinstance(child, Tag):
                if child.name in ['h1', 'h2', 'h3', 'h4']:
                    level = int(child.name[1])
                    md += f"\n\n{'#' * level} {child.get_text(strip=True)}\n\n"
                elif child.name == 'p':
                    md += f"\n\n{child.get_text(separator=' ', strip=True)}\n\n"
                elif child.name in ['pre', 'div'] and ('highlight' in child.get('class', []) or child.name == 'pre'):
                    # Capture code blocks
                    code = child.get_text()
                    md += f"\n\n```python\n{code.strip()}\n```\n\n"
                elif child.name == 'code':
                    md += f" `{child.get_text(strip=True)}` "
                elif child.name == 'li':
                    md += f"\n* {child.get_text(strip=True)}"
                elif child.name == 'table':
                    md += "\n\n[Table Content Ignored for Plain Markdown]\n\n"
                else:
                    # Recursive call for nested divs/sections
                    md += self.smarter_markdown(child)
        return md

    def scrape(self) -> List[ScrapedDocument]:
        all_urls = self.discover_links()
        documents = []

        for i, url in enumerate(all_urls):
            print(f"📄 [{i+1}/{len(all_urls)}] Scraping: {url}")
            try:
                res = requests.get(url, timeout=10)
                soup = BeautifulSoup(res.text, 'html.parser')
                
                # Target the article
                article = soup.find('article', class_='bd-article')
                if not article:
                    continue

                # Cleanup junk
                for junk in article(['script', 'style', 'nav', 'headerlink', 'aside']):
                    junk.decompose()

                # Generate high-quality content
                markdown_body = self.smarter_markdown(article)
                
                # Capture Title
                h1 = soup.find('h1')
                title = h1.get_text(strip=True) if h1 else f"Pandas Page {i}"

                documents.append(ScrapedDocument(
                    url=url,
                    title=title,
                    framework=self.framework_name,
                    markdown_content=markdown_body
                ))
                
                # Polite delay
                time.sleep(0.5) 
            except Exception as e:
                print(f"⚠️ Error on {url}: {e}")

        return documents