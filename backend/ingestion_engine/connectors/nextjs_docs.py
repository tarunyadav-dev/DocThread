import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup, Tag, NavigableString
from typing import List
from urllib.parse import urljoin
from ingestion_engine.connectors.base_connector import BaseScraperConnector, ScrapedDocument

class NextjsScraper(BaseScraperConnector):
    def __init__(self):
        super().__init__(
            framework_name="Next.js", 
            start_urls=["https://nextjs.org/docs"]
        )
        self.base_domain = "https://nextjs.org"

    async def discover_links(self, page) -> List[str]:
        """Deep scans the Next.js sidebar for all documentation links."""
        print("🔍 Deep-scanning Next.js Documentation sidebar...")
        await page.goto(self.start_urls[0], wait_until="networkidle")
        
        # Give the complex Next.js sidebar a moment to fully hydrate its routing tree
        await asyncio.sleep(2) 
        
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        
        # We look for all links that live under the /docs path
        all_links = soup.find_all('a', href=True)
        
        for a in all_links:
            href = a['href']
            # Target both App Router and Pages Router docs, plus architecture
            if href.startswith('/docs/'):
                full_url = urljoin(self.base_domain, href)
                clean_url = full_url.split('#')[0] # Remove hash anchors
                if clean_url not in links:
                    links.append(clean_url)
        
        print(f"🕸️ Found {len(links)} nested Next.js documentation pages.")
        return links

    def smarter_markdown(self, element) -> str:
        """Advanced recursive converter for Next.js complex layouts."""
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
                
                # Next.js specific warning/info callouts (Usually divs with specific data-attributes or classes)
                elif child.name == 'div' and 'data-callout' in child.attrs:
                    callout_type = child.get('data-callout', 'Note').title()
                    md += f"\n\n> **{callout_type}:** {child.get_text(strip=True)}\n\n"
                
                # Handle Code Blocks (Next.js uses pre with data-language)
                elif child.name == 'pre' or child.name == 'code' and child.parent.name != 'pre':
                    if child.name == 'pre':
                        code = child.get_text()
                        lang = child.get('data-language', 'typescript')
                        md += f"\n\n```{lang}\n{code.strip()}\n```\n\n"
                    else:
                        md += f" `{child.get_text(strip=True)}` "
                
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
            # Launch with a standard User-Agent so Vercel's firewalls don't block us
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            
            urls = await self.discover_links(page)
            
            for i, url in enumerate(urls):
                print(f"📄 [{i+1}/{len(urls)}] Scraping Next.js: {url}")
                try:
                    await page.goto(url, wait_until="domcontentloaded")
                    # Next.js main content usually lives in a <main> or <article> tag
                    try:
                        await page.wait_for_selector('main', timeout=8000)
                    except:
                        await page.wait_for_selector('article', timeout=8000)
                    
                    html = await page.content()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    article = soup.find('main') or soup.find('article')
                    if not article: 
                        print(f"⚠️ Could not find main content for {url}")
                        continue

                    # Clean up interactive sandboxes, sidebars, TOCs
                    for junk in article.find_all(['nav', 'button', 'script', 'iframe', 'div', 'aside']):
                        # Target Table of Contents or specific UI components to strip
                        if 'toc' in junk.get('class', []) or 'navigation' in junk.get('class', []):
                            junk.decompose()
                        elif junk.name in ['nav', 'button', 'script', 'iframe', 'aside']:
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
                    
                    # Polite sleep
                    await asyncio.sleep(0.8)
                except Exception as e:
                    print(f"⚠️ Skipping {url} due to error: {e}")
            
            await browser.close()
        return documents

    def scrape(self) -> List[ScrapedDocument]:
        return asyncio.run(self._scrape_all())