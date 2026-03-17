import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup, Tag, NavigableString
from typing import List
from urllib.parse import urljoin
from ingestion_engine.connectors.base_connector import BaseScraperConnector, ScrapedDocument

class AngularScraper(BaseScraperConnector):
    def __init__(self):
        super().__init__(
            framework_name="Angular", 
            # We seed the crawler with the main sections of angular.dev
            start_urls=[
                "https://angular.dev/overview",
                "https://angular.dev/guide",
                "https://angular.dev/reference",
                "https://angular.dev/tutorials"
            ]
        )
        self.base_domain = "https://angular.dev"

    async def discover_links(self, page) -> List[str]:
        """Scans the Angular.dev sidebars across core sections to map the entire documentation."""
        print("🔍 Deep-scanning Angular Documentation sidebars...")
        links = set()

        # Visit each core section to ensure the dynamic sidebar loads its specific tree
        for start_url in self.start_urls:
            try:
                await page.goto(start_url, wait_until="networkidle")
                # Give Angular's hydration and custom elements time to render
                await asyncio.sleep(2) 
                
                html = await page.content()
                soup = BeautifulSoup(html, 'html.parser')
                
                # angular.dev uses a massive navigation tree. We grab all links.
                all_links = soup.find_all('a', href=True)
                
                for a in all_links:
                    href = a['href']
                    # Target the core documentation directories
                    if href.startswith('/guide') or href.startswith('/reference') or href.startswith('/tutorials') or href.startswith('/overview'):
                        full_url = urljoin(self.base_domain, href)
                        clean_url = full_url.split('#')[0] # Remove hash anchors
                        links.add(clean_url)
            except Exception as e:
                print(f"⚠️ Link discovery error on {start_url}: {e}")

        links_list = list(links)
        print(f"🕸️ Found {len(links_list)} complete Angular pages.")
        return links_list

    def smarter_markdown(self, element) -> str:
        """Advanced recursive converter optimized for Angular's custom Web Components."""
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
                
                # Angular Callouts / Info Boxes (Often custom classes like docs-callout)
                elif 'docs-callout' in child.get('class', []) or child.name == 'docs-callout':
                    md += f"\n\n> **Note:** {child.get_text(separator=' ', strip=True)}\n\n"
                
                # Angular Code Blocks (Angular.dev uses a custom <docs-code-block> or <docs-code> tag)
                elif child.name in ['docs-code-block', 'docs-code', 'pre']:
                    code = child.get_text()
                    # Try to infer language if provided, otherwise default to typescript for Angular
                    lang = child.get('language', 'typescript')
                    md += f"\n\n```{lang}\n{code.strip()}\n```\n\n"
                
                # Regular Text
                elif child.name == 'p':
                    md += f"\n\n{child.get_text(separator=' ', strip=True)}\n\n"
                
                # Lists
                elif child.name == 'li':
                    md += f"\n* {child.get_text(separator=' ', strip=True)}"
                
                # Inline code
                elif child.name == 'code' and child.parent.name not in ['pre', 'docs-code-block']:
                    md += f" `{child.get_text(strip=True)}` "
                
                # Ignore SVG icons
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
                print(f"📄 [{i+1}/{len(urls)}] Scraping Angular: {url}")
                try:
                    await page.goto(url, wait_until="domcontentloaded")
                    
                    # Angular.dev usually wraps core content in <main> or a custom <docs-viewer> tag
                    try:
                        await page.wait_for_selector('main', timeout=10000)
                    except:
                        await page.wait_for_selector('docs-viewer', timeout=10000)
                    
                    # Short sleep for signals/DOM to finish settling
                    await asyncio.sleep(1)
                    
                    html = await page.content()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    article = soup.find('main') or soup.find('docs-viewer') or soup.find('article')
                    if not article: 
                        print(f"⚠️ Could not find main content for {url}")
                        continue

                    # Clean up the noise (TOC, navigation menus, header links)
                    for junk in article.find_all(['nav', 'button', 'script', 'iframe', 'docs-breadcrumb', 'docs-table-of-contents']):
                        junk.decompose()
                        
                    # Also strip sidebars explicitly if they bleed into <main>
                    for aside in article.find_all('aside'):
                        aside.decompose()

                    markdown_content = self.smarter_markdown(article)
                    h1 = soup.find('h1')
                    title = h1.get_text(strip=True) if h1 else url.split('/')[-1]

                    documents.append(ScrapedDocument(
                        url=url,
                        title=title,
                        framework=self.framework_name,
                        markdown_content=markdown_content
                    ))
                    
                except Exception as e:
                    print(f"⚠️ Skipping {url} due to error: {e}")
            
            await browser.close()
        return documents

    def scrape(self) -> List[ScrapedDocument]:
        return asyncio.run(self._scrape_all())