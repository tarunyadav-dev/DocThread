import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup, Tag, NavigableString
from typing import List
from urllib.parse import urljoin
from ingestion_engine.connectors.base_connector import BaseScraperConnector, ScrapedDocument

class ReactScraper(BaseScraperConnector):
    def __init__(self):
        super().__init__(
            framework_name="React", 
            start_urls=["https://react.dev/reference/react"]
        )

    async def discover_links(self, page) -> List[str]:
        """Deep scans the React sidebar for all nested reference links."""
        print("🔍 Deep-scanning React Reference sidebar...")
        await page.goto(self.start_urls[0], wait_until="networkidle")
        
        # Give the sidebar a moment to fully hydrate
        await asyncio.sleep(2) 
        
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        
        # React Dev Sidebar usually sits in a <nav> or a div with specific classes
        # We look for all links that live under the /reference/react path
        all_side_links = soup.find_all('a', href=True)
        
        for a in all_side_links:
            href = a['href']
            # We target Hooks, Components, and APIs
            if href.startswith('/reference/react/'):
                full_url = urljoin("https://react.dev", href)
                # Avoid anchors like #usage
                clean_url = full_url.split('#')[0]
                if clean_url not in links:
                    links.append(clean_url)
        
        print(f"🕸️ Found {len(links)} nested React reference pages.")
        return links # Removed the [:10] limit - let's go for the whole thing!

    def smarter_markdown(self, element) -> str:
        """Advanced recursive converter for React's complex layout."""
        md = ""
        for child in element.children:
            if isinstance(child, NavigableString):
                text = str(child).strip()
                if text: md += f" {text} "
            elif isinstance(child, Tag):
                # Handle Headers
                if child.name in ['h1', 'h2', 'h3', 'h4']:
                    level = int(child.name[1])
                    md += f"\n\n{'#' * level} {child.get_text(strip=True)}\n\n"
                
                # Handle Special React Boxes (Pitfalls/Notes)
                elif 'bg-opacity-10' in str(child.get('class', [])): # Common React 'Note' box
                    md += f"\n\n> **Note:** {child.get_text(strip=True)}\n\n"
                
                # Handle Code Blocks
                elif child.name == 'pre' or child.get('data-language'):
                    code = child.get_text()
                    md += f"\n\n```jsx\n{code.strip()}\n```\n\n"
                
                # Handle Regular Text
                elif child.name == 'p':
                    md += f"\n\n{child.get_text(strip=True)}\n\n"
                
                # Handle Lists
                elif child.name == 'li':
                    md += f"\n* {child.get_text(strip=True)}"
                
                # Inline code
                elif child.name == 'code':
                    md += f" `{child.get_text(strip=True)}` "
                
                # Continue Recursing
                else:
                    md += self.smarter_markdown(child)
        return md

    async def _scrape_all(self) -> List[ScrapedDocument]:
        documents = []
        async with async_playwright() as p:
            # We launch with a standard User-Agent so we don't look like a bot
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            
            urls = await self.discover_links(page)
            
            for i, url in enumerate(urls):
                print(f"📄 [{i+1}/{len(urls)}] Scraping React: {url}")
                try:
                    # Navigate and wait for content
                    await page.goto(url, wait_until="domcontentloaded")
                    # React pages can be heavy, wait for the article specifically
                    await page.wait_for_selector('article', timeout=10000)
                    
                    html = await page.content()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    article = soup.find('article')
                    if not article: continue

                    # Clean up interactive sandboxes and buttons
                    for junk in article.find_all(['nav', 'button', 'script', 'iframe']):
                        junk.decompose()

                    markdown_content = self.smarter_markdown(article)
                    h1 = soup.find('h1')
                    title = h1.get_text(strip=True) if h1 else url.split('/')[-1]

                    documents.append(ScrapedDocument(
                        url=url,
                        title=title,
                        framework=self.framework_name,
                        markdown_content=markdown_content
                    ))
                    
                    # Small sleep to prevent rate limiting
                    await asyncio.sleep(0.8)
                except Exception as e:
                    print(f"⚠️ Skipping {url} due to error: {e}")
            
            await browser.close()
        return documents

    def scrape(self) -> List[ScrapedDocument]:
        return asyncio.run(self._scrape_all())