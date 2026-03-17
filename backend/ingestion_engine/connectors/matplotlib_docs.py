import requests
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup, Tag, NavigableString
from typing import List
from ingestion_engine.connectors.base_connector import BaseScraperConnector, ScrapedDocument

class MatplotlibScraper(BaseScraperConnector):
    def __init__(self):
        super().__init__(
            framework_name="Matplotlib", 
            # Start at the root of the stable documentation
            start_urls=["https://matplotlib.org/stable/index.html"]
        )
        self.base_domain = "https://matplotlib.org/stable/"
        
        # Prevent the crawler from downloading zip files, raw code, or useless indexes
        self.blacklist = [
            '_sources/', 
            '_downloads/', 
            '/search.html', 
            '/genindex.html', 
            '/py-modindex.html',
            '.zip', 
            '.ipynb', 
            '.py'
        ]

    def is_valid_link(self, url: str) -> bool:
        """Filters out non-stable docs, external links, and blacklisted file types."""
        if not url.startswith(self.base_domain):
            return False
        
        # We only want to parse HTML documentation pages
        if not url.split('?')[0].endswith('.html') and not url.endswith('/'):
            return False
            
        for bad_path in self.blacklist:
            if bad_path in url:
                return False
                
        return True

    def discover_links(self) -> List[str]:
        """Deep Crawler (BFS) to map the massive Matplotlib documentation and galleries."""
        print("🔍 Deploying Deep-Crawler for Matplotlib Documentation...")
        print("⚠️  Note: Matplotlib includes extensive galleries and APIs. This may find hundreds of pages.")
        
        visited = set([self.start_urls[0]])
        queue = [self.start_urls[0]]
        all_links = []

        while queue:
            current_url = queue.pop(0)
            
            # Add to scraping list
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
                
        print(f"🕸️ Spider complete! Found {len(all_links)} Matplotlib pages.")
        return all_links

    def smarter_markdown(self, element) -> str:
        """Recursive converter optimized for Sphinx and Sphinx-Gallery elements."""
        md = ""
        for child in element.children:
            if isinstance(child, NavigableString):
                text = str(child).strip()
                if text:
                    md += f" {text} "
            elif isinstance(child, Tag):
                # Headers
                if child.name in ['h1', 'h2', 'h3', 'h4', 'h5']:
                    level = int(child.name[1])
                    md += f"\n\n{'#' * level} {child.get_text(strip=True)}\n\n"
                
                # Sphinx Admonitions (Notes, Warnings)
                elif child.name == 'div' and 'admonition' in child.get('class', []):
                    title_tag = child.find('p', class_='admonition-title')
                    title = title_tag.get_text(strip=True) if title_tag else "Note"
                    md += f"\n\n> **{title}:** "
                    content = child.get_text(separator=' ', strip=True).replace(title, '', 1)
                    md += f"{content}\n\n"
                
                # Code Blocks (Sphinx typically uses div.highlight > pre)
                elif child.name == 'div' and 'highlight' in child.get('class', []):
                    pre = child.find('pre')
                    if pre:
                        code = pre.get_text()
                        md += f"\n\n```python\n{code.strip()}\n```\n\n"
                elif child.name == 'pre' and not child.find_parent('div', class_='highlight'):
                     code = child.get_text()
                     md += f"\n\n```text\n{code.strip()}\n```\n\n"
                
                # Paragraphs
                elif child.name == 'p':
                    # Prevent duplicating admonition titles
                    if 'admonition-title' not in child.get('class', []):
                        md += f"\n\n{child.get_text(separator=' ', strip=True)}\n\n"
                
                # Inline Code
                elif child.name in ['code', 'span'] and ('pre' in child.get('class', []) or child.name == 'code'):
                    if child.parent.name != 'pre':
                        md += f" `{child.get_text(strip=True)}` "
                
                # Lists
                elif child.name == 'li':
                    md += f"\n* {child.get_text(strip=True)}"
                
                # Recurse for nested divs (like sections)
                elif child.name in ['div', 'section', 'article']:
                    # Skip gallery thumbnails visually, but keep their text if needed
                    if 'sphx-glr-thumbcontainer' in child.get('class', []):
                        continue
                    md += self.smarter_markdown(child)
                else:
                    md += self.smarter_markdown(child)
        return md

    def scrape(self) -> List[ScrapedDocument]:
        all_urls = self.discover_links()
        documents = []

        for i, url in enumerate(all_urls):
            print(f"📄 [{i+1}/{len(all_urls)}] Scraping Matplotlib: {url}")
            try:
                res = requests.get(url, timeout=10)
                soup = BeautifulSoup(res.text, 'html.parser')
                
                # Matplotlib usually stores the main content in a div with role="main" or class="bd-article"
                article = soup.find('div', role='main') or soup.find('article', class_='bd-article')
                if not article:
                    continue

                # Clean up junk (navigation menus, right-side TOCs, header anchor links)
                for junk in article.find_all(['nav', 'script', 'style', 'a'], class_=['headerlink', 'sphinxsidebar']):
                    junk.decompose()
                    
                # Decompose Sphinx-Gallery download buttons (they add useless text to the RAG)
                for download_btn in article.find_all('div', class_='sphx-glr-download'):
                    download_btn.decompose()

                markdown_body = self.smarter_markdown(article)
                
                h1 = soup.find('h1')
                title = h1.get_text(strip=True) if h1 else f"Matplotlib Page {i}"

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