import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup, Tag, NavigableString
from typing import List
from urllib.parse import urljoin
from ingestion_engine.connectors.base_connector import BaseScraperConnector, ScrapedDocument

class DockerScraper(BaseScraperConnector):
    def __init__(self):
        super().__init__(
            framework_name="Docker", 
            # Seed the crawler with the highest-value hubs
            start_urls=[
                "https://docs.docker.com/manuals/",
                "https://docs.docker.com/reference/"
            ]
        )
        self.base_domain = "https://docs.docker.com"

    async def discover_links(self, page) -> List[str]:
        """Deep scans the Docker documentation hubs to map the CLI and manual sections."""
        print("🔍 Deep-scanning Docker Documentation sidebars...")
        links = set()

        for start_url in self.start_urls:
            try:
                await page.goto(start_url, wait_until="networkidle")
                # Give the complex Docker UI time to render its sidebars
                await asyncio.sleep(2) 
                
                html = await page.content()
                soup = BeautifulSoup(html, 'html.parser')
                
                all_links = soup.find_all('a', href=True)
                
                for a in all_links:
                    href = a['href']
                    # Target the core manuals, guides, and reference materials
                    if href.startswith('/manuals/') or href.startswith('/reference/') or href.startswith('/guides/'):
                        full_url = urljoin(self.base_domain, href)
                        clean_url = full_url.split('#')[0] # Remove hash anchors
                        
                        # Filter out raw JSON endpoints or GitHub edit links
                        if not clean_url.endswith('.json') and 'github.com' not in clean_url:
                            links.add(clean_url)
            except Exception as e:
                print(f"⚠️ Link discovery error on {start_url}: {e}")

        links_list = list(links)
        print(f"🕸️ Found {len(links_list)} complete Docker pages.")
        return links_list

    def smarter_markdown(self, element) -> str:
        """Advanced recursive converter optimized for Docker's layout and tabs."""
        md = ""
        for child in element.children:
            if isinstance(child, NavigableString):
                text = str(child).strip()
                if text: md += f" {text} "
            elif isinstance(child, Tag):
                # Headers
                if child.name in ['h1', 'h2', 'h3', 'h4', 'h5']:
                    level = int(child.name[1])
                    md += f"\n\n{'#' * level} {child.get_text(strip=True)}\n\n"
                
                # Docker Admonitions (Note, Warning, Tip)
                elif child.name == 'blockquote':
                    md += f"\n\n> {child.get_text(separator=' ', strip=True)}\n\n"
                
                # Code Blocks (Docker uses standard pre > code combinations)
                elif child.name == 'pre':
                    code = child.get_text()
                    # Try to infer if it's a console command vs YAML
                    lang = "bash" if "$" in code[:10] else "yaml"
                    md += f"\n\n```{lang}\n{code.strip()}\n```\n\n"
                
                # Regular Text
                elif child.name == 'p':
                    md += f"\n\n{child.get_text(separator=' ', strip=True)}\n\n"
                
                # Lists
                elif child.name == 'li':
                    md += f"\n* {child.get_text(separator=' ', strip=True)}"
                
                # Inline code
                elif child.name == 'code' and child.parent.name != 'pre':
                    md += f" `{child.get_text(strip=True)}` "
                
                # Ignore SVG icons commonly used in Docker's UI
                elif child.name == 'svg':
                    continue
                
                # Continue Recursing
                else:
                    md += self.smarter_markdown(child)
        return md

    async def _scrape_all(self) -> List[ScrapedDocument]:
        documents = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            
            urls = await self.discover_links(page)
            
            for i, url in enumerate(urls):
                print(f"📄 [{i+1}/{len(urls)}] Scraping Docker: {url}")
                try:
                    await page.goto(url, wait_until="domcontentloaded")
                    
                    # Docker docs usually wrap core content in a <main> tag
                    try:
                        await page.wait_for_selector('main', timeout=10000)
                    except:
                        pass # Fallback to parsing the body if main is missing
                    
                    # Short sleep for tabbed content to hydrate
                    await asyncio.sleep(1)
                    
                    html = await page.content()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    article = soup.find('main') or soup.find('body')
                    if not article: 
                        print(f"⚠️ Could not find main content for {url}")
                        continue

                    # Clean up the noise (Sidebars, TOCs, Headers, Footers)
                    for junk in article.find_all(['nav', 'header', 'footer', 'script', 'iframe', 'aside']):
                        junk.decompose()
                        
                    # Remove the "On this page" right-hand TOC specifically
                    for toc in article.find_all('div', class_='toc'):
                        toc.decompose()

                    markdown_content = self.smarter_markdown(article)
                    h1 = soup.find('h1')
                    title = h1.get_text(strip=True) if h1 else url.split('/')[-1]

                    documents.append(ScrapedDocument(
                        url=url,
                        title=title,
                        framework=self.framework_name,
                        markdown_content=markdown_content
                    ))
                    
                    # Polite sleep to avoid rate limiting
                    await asyncio.sleep(0.8)
                    
                except Exception as e:
                    print(f"⚠️ Skipping {url} due to error: {e}")
            
            await browser.close()
        return documents

    def scrape(self) -> List[ScrapedDocument]:
        return asyncio.run(self._scrape_all())