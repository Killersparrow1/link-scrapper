#!/usr/bin/env python3
"""
Interactive Forum Thread Scraper
Menu-driven interface for scraping links from forum threads.
"""

import argparse
import asyncio
import json
import os
import re
import sqlite3
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from urllib.parse import urlparse, urljoin, parse_qs, urlencode, urlunparse

import aiohttp
from bs4 import BeautifulSoup

# Optional dependencies with fallback
try:
    from tqdm.asyncio import tqdm_asyncio
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

try:
    from playwright.async_api import async_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False
    # Simple fallback
    class tqdm:
        def __init__(self, *args, **kwargs):
            self.total = kwargs.get('total', 0)
            self.desc = kwargs.get('desc', '')
            self.n = 0
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def update(self, n=1):
            self.n += n
            if self.total:
                print(f"\r{self.desc}: {self.n}/{self.total}", end="", flush=True)
        def set_description(self, desc):
            self.desc = desc
            print(f"\r{desc}: {self.n}/{self.total}", end="", flush=True)
        def close(self):
            print()


class CookieExtractor:
    BROWSER_PATHS = {
        "firefox": [
            "~/.config/mozilla/firefox/*/cookies.sqlite",
            "~/.mozilla/firefox/*/cookies.sqlite",
            "~/snap/firefox/common/.mozilla/firefox/*/cookies.sqlite",
            "~/.var/app/org.mozilla.firefox/.mozilla/firefox/*/cookies.sqlite",
        ],
        "chrome": [
            "~/.config/google-chrome/*/Cookies",
            "~/.config/chromium/*/Cookies",
            "~/snap/chromium/common/.config/chromium/*/Cookies",
        ],
        "brave": [
            "~/.config/BraveSoftware/Brave-Browser/*/Cookies",
        ],
        "edge": [
            "~/.config/microsoft-edge/*/Cookies",
        ],
    }
    
    def __init__(self, browser: str = "firefox"):
        self.browser = browser.lower()
    
    def get_cookies(self, domain: str) -> Dict[str, str]:
        cookies = {}
        paths = self.BROWSER_PATHS.get(self.browser, [])
        
        for pattern in paths:
            expanded = Path(pattern).expanduser()
            for db_path in expanded.parent.glob(expanded.name):
                try:
                    cookies.update(self._extract_from_db(db_path, domain))
                except Exception:
                    continue
        return cookies
    
    def _extract_from_db(self, db_path: Path, domain: str) -> Dict[str, str]:
        cookies = {}
        with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            import shutil
            shutil.copy2(db_path, tmp_path)
            conn = sqlite3.connect(tmp_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Try multiple query patterns for different browser cookie schemas
            queries = [
                # Firefox
                ("SELECT name, value, host FROM moz_cookies WHERE host LIKE ?", ["name", "value", "host"]),
                # Chrome/Chromium/Brave/Edge (new schema)
                ("SELECT name, value, host_key FROM cookies WHERE host_key LIKE ?", ["name", "value", "host_key"]),
                # Older Chrome schema
                ("SELECT name, value, domain FROM cookies WHERE domain LIKE ?", ["name", "value", "domain"]),
            ]
            
            for query, cols in queries:
                try:
                    cursor.execute(query, (f"%{domain}%",))
                    for row in cursor.fetchall():
                        # Normalize column access
                        name = row[cols[0]]
                        value = row[cols[1]]
                        if name and value:
                            cookies[name] = value
                    if cookies:
                        break
                except sqlite3.OperationalError:
                    continue
            
            conn.close()
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        return cookies


class ThreadScraper:
    IMG_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg"}
    VID_EXTS = {".mp4", ".webm", ".mkv", ".avi", ".mov", ".flv", ".m4v", ".mpeg", ".mpg", ".ogv"}
    
    IMG_DOMAINS = [
        "imagepond.net/i/", "goonbox.cr/img/", "imagebam.com/view/",
        "simp6.cuckcapital.cr/images", "cosplayrule34.com/images",
        "media.imagepond.net/media/images", "catbox.moe", "imgbox.com",
        "postimg.cc", "ibb.co", "files.catbox.moe", "jpghub.nl",
        "pbs.twimg.com", "preview.redd.it", "img.kiwi", "i.postimg.cc",
        "i.imgur.com", "pixhost.to", "imgur.com", "static.hentai-cosplays.com",
    ]
    
    VID_DOMAINS = [
        "imagepond.net/videos/", "turbo.cr/embed/", "pornmz.com/video",
        "eporner.com/video", "beeg.com/", "bunkr.cr/a/", "bunkr.si/f/",
        "bunkr.pk/f/", "bunkr.media/f/", "bunkr.ac/v/", "bunkr.ax/v/",
        "bunkr.black/v/", "bunkr.cat/v/", "bunkr.fi/f/", "bunkr.ph/a/",
        "bunkr.red/f/", "bunkrrr.org/v/", "bunkrrr.org/a/", "bunkrrr.org/f/",
        "bunkr.si/a/", "bunkr.site/a/", "bunkr.site/f/", "bunkr.si/v/",
        "bunkr.sk/a/", "bunkr.sk/v/", "filester.me/f/", "filester.si/d/",
        "gofile.io/d/", "pixeldrain.com/l/", "pixeldrain.com/u/",
        "saint2.cr/embed/", "saint2.su/embed/", "turbo.cr/v/",
        "fileditchfiles.me", "stream.bunkr.", "erome.com/a/",
        "cyberdrop.me/f/", "cyberfile.me/", "mega.nz/file/",
        "coomer.party/", "thothub.ch/videos/", "pornforce.com/",
        "pornolab.net/", "xvideos.com/video", "pornhub.com/view_video",
        "redgifs.com/users/", "onlyfans.com/", "manyvids.com/Video/",
    ]
    
    # UTM and tracking parameters to strip
    TRACKING_PARAMS = {
        "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
        "fbclid", "gclid", "ref", "source", "ref_src", "ref_url",
        "igshid", "si", "sfns", "tt_medium", "tt_source",
        "mc_cid", "mc_eid", "_hsmi", "_hsenc",
    }
    
    def __init__(self, output_dir: Path, browser: str = "firefox", use_playwright: bool = False):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cookie_extractor = CookieExtractor(browser)
        self.session: Optional[aiohttp.ClientSession] = None
        self.all_urls: Set[str] = set()
        self.image_urls: List[str] = []
        self.video_urls: List[str] = []
        self.post_urls: List[str] = []  # Individual post permalinks
        self.other_urls: List[str] = []
        self.thread_url = ""
        self.thread_title = ""
        self.thread_id = ""
        self.request_delay = 1.0
        self.max_retries = 3
        self.checkpoint_file = self.output_dir / ".checkpoint.json"
        self.use_playwright = use_playwright and HAS_PLAYWRIGHT
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()
    
    def _extract_thread_info(self, thread_url: str):
        """Extract thread title and ID from URL."""
        parsed = urlparse(thread_url)
        path = parsed.path
        
        id_match = re.search(r'\.(\d+)(?:/|$)', path)
        if id_match:
            self.thread_id = id_match.group(1)
        
        title_match = re.search(r'/threads/([^/.]+)', path)
        if title_match:
            raw_title = title_match.group(1)
            self.thread_title = raw_title.replace('-', ' ').replace('_', ' ')
        else:
            self.thread_title = "thread"
        
        self.thread_title = re.sub(r'[<>:"/\\|?*]', '', self.thread_title)
        self.thread_title = re.sub(r'\s+', '_', self.thread_title.strip())
        if len(self.thread_title) > 100:
            self.thread_title = self.thread_title[:100]
    
    def _get_output_prefix(self) -> str:
        if self.thread_title:
            return self.thread_title
        return f"thread_{self.thread_id}" if self.thread_id else "thread"
    
    def normalize_url(self, url: str, base_url: str = "") -> str:
        """Normalize URL: resolve relative, strip tracking params, fragments."""
        if not url:
            return ""
        
        # Resolve relative URLs
        if base_url and not url.startswith(("http://", "https://", "//")):
            url = urljoin(base_url, url)
        
        # Handle protocol-relative URLs
        if url.startswith("//"):
            url = "https:" + url
        
        try:
            parsed = urlparse(url)
        except Exception:
            return ""
        
        # Strip fragment
        parsed = parsed._replace(fragment="")
        
        # Strip tracking parameters
        query_params = parse_qs(parsed.query, keep_blank_values=True)
        filtered_params = {
            k: v for k, v in query_params.items() 
            if k.lower() not in self.TRACKING_PARAMS
        }
        parsed = parsed._replace(query=urlencode(filtered_params, doseq=True))
        
        # Reconstruct URL
        normalized = urlunparse(parsed)
        
        # Strip trailing slash for non-root paths
        if normalized.endswith("/") and parsed.path != "/":
            normalized = normalized[:-1]
        
        return normalized
    
    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and not empty/junk."""
        if not url or len(url) < 10:
            return False
        if url.startswith(("data:", "javascript:", "mailto:", "tel:", "#")):
            return False
        if re.match(r'^https?://', url) is None:
            return False
        return True
    
    def is_post_permalink(self, url: str) -> bool:
        """Check if URL is a post permalink (e.g., /post-1234567)."""
        return bool(re.search(r'/post-\d+', url))
    
    def classify_url(self, url: str) -> str:
        # Check for post permalinks first
        if self.is_post_permalink(url):
            return "post"
        parsed = urlparse(url)
        path = parsed.path.lower()
        for ext in self.IMG_EXTS:
            if path.endswith(ext):
                return "image"
        for ext in self.VID_EXTS:
            if path.endswith(ext):
                return "video"
        full_url = url.lower()
        for domain in self.IMG_DOMAINS:
            if domain in full_url:
                return "image"
        for domain in self.VID_DOMAINS:
            if domain in full_url:
                return "video"
        return "other"
    
    def add_url(self, url: str):
        if url in self.all_urls:
            return
        self.all_urls.add(url)
        category = self.classify_url(url)
        if category == "image":
            self.image_urls.append(url)
        elif category == "video":
            self.video_urls.append(url)
        elif category == "post":
            self.post_urls.append(url)
        else:
            self.other_urls.append(url)
    
    async def fetch_page_with_retry(self, url: str, cookies: Dict[str, str]) -> str:
        """Fetch page with retry logic and exponential backoff."""
        headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0"}
        cookie_header = "; ".join(f"{k}={v}" for k, v in cookies.items())
        if cookie_header:
            headers["Cookie"] = cookie_header
        
        for attempt in range(self.max_retries):
            try:
                async with self.session.get(url, headers=headers) as resp:
                    if resp.status == 429:  # Rate limited
                        retry_after = int(resp.headers.get("Retry-After", 2 ** attempt))
                        print(f"[!] Rate limited (429), waiting {retry_after}s...")
                        await asyncio.sleep(retry_after)
                        continue
                    elif resp.status >= 500:
                        raise aiohttp.ClientError(f"Server error: {resp.status}")
                    return await resp.text()
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt == self.max_retries - 1:
                    raise
                wait_time = 2 ** attempt
                print(f"[!] Attempt {attempt + 1} failed: {e}, retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
        
        raise Exception(f"Failed to fetch {url} after {self.max_retries} attempts")
    
    def extract_links(self, html: str, base_url: str) -> List[str]:
        """Extract all links from HTML with improved detection."""
        soup = BeautifulSoup(html, "lxml")  # Use lxml for speed
        links = []
        
        # Check various tags and attributes
        for tag in soup.find_all(["a", "img", "video", "source", "iframe", "embed", "object"]):
            for attr in ["href", "src", "data-src", "data-original", "data-url", "data-lazy", "data-srcset"]:
                val = tag.get(attr)
                if val:
                    # Handle srcset (comma-separated URLs with descriptors)
                    if attr == "data-srcset" or attr == "srcset":
                        for part in val.split(","):
                            url = part.strip().split()[0]
                            if url:
                                links.append(url)
                    else:
                        links.append(val)
        
        # Extract from style attributes (background images)
        for tag in soup.find_all(style=True):
            style = tag.get("style", "")
            urls = re.findall(r'url\(["\']?([^"\')]+)["\']?\)', style)
            links.extend(urls)
        
        # Extract from <script> tags
        for script in soup.find_all("script"):
            if script.string:
                # Find URLs in JavaScript
                script_urls = re.findall(r'(?:https?://|//)[^\s<>"\'\)\]]+', script.string)
                links.extend(script_urls)
        
        # Extract from text content (better regex)
        text = soup.get_text()
        # Match URLs but exclude trailing punctuation
        url_pattern = re.compile(r'https?://[^\s<>"\']+?(?=[\s<>"\'\)\]]|$)')
        links.extend(url_pattern.findall(text))
        
        # Normalize and filter
        normalized = []
        for link in links:
            norm = self.normalize_url(link, base_url)
            if self.is_valid_url(norm):
                normalized.append(norm)
        
        return normalized
    
    def save_checkpoint(self, page: int):
        """Save current scraping progress."""
        checkpoint = {
            "page": page,
            "all_urls": list(self.all_urls),
            "image_urls": self.image_urls,
            "video_urls": self.video_urls,
            "post_urls": self.post_urls,
            "other_urls": self.other_urls,
            "thread_url": self.thread_url,
            "thread_title": self.thread_title,
            "thread_id": self.thread_id,
            "timestamp": time.time(),
        }
        try:
            with open(self.checkpoint_file, "w") as f:
                json.dump(checkpoint, f)
        except Exception as e:
            print(f"[!] Failed to save checkpoint: {e}")
    
    def load_checkpoint(self) -> Optional[int]:
        """Load checkpoint and restore state. Returns last scraped page or 0."""
        if not self.checkpoint_file.exists():
            return 0
        
        try:
            with open(self.checkpoint_file, "r") as f:
                checkpoint = json.load(f)
            
            # Verify it's for the same thread
            if checkpoint.get("thread_url") != self.thread_url:
                return 0
            
            self.all_urls = set(checkpoint.get("all_urls", []))
            self.image_urls = checkpoint.get("image_urls", [])
            self.video_urls = checkpoint.get("video_urls", [])
            self.post_urls = checkpoint.get("post_urls", [])
            self.other_urls = checkpoint.get("other_urls", [])
            
            last_page = checkpoint.get("page", 0)
            print(f"[+] Resumed from checkpoint: page {last_page}, {len(self.all_urls)} URLs already collected")
            return last_page
        except Exception as e:
            print(f"[!] Failed to load checkpoint: {e}")
            return 0
    
    def detect_pagination_pattern(self, html: str, base_url: str) -> Optional[str]:
        """Detect pagination pattern from HTML."""
        soup = BeautifulSoup(html, "lxml")
        
        # Look for pagination links
        pagination_selectors = [
            ".pagination a", ".pageNav a", ".pager a", 
            "[class*='page'] a", "[class*='pagination'] a",
            "nav.pagination a", "ul.pagination a"
        ]
        
        page_urls = set()
        for selector in pagination_selectors:
            for link in soup.select(selector):
                href = link.get("href")
                if href:
                    page_urls.add(urljoin(base_url, href))
        
        if not page_urls:
            return None
        
        # Analyze URL patterns
        patterns = [
            (r'/page-(\d+)', '/page-{}'),
            (r'/p(\d+)', '/p{}'),
            (r'[?&]page=(\d+)', '?page={}'),
            (r'/(\d+)(?:/|$)', '/{}'),
        ]
        
        for page_url in page_urls:
            for pattern, template in patterns:
                match = re.search(pattern, page_url)
                if match:
                    # Verify it's a page number (not thread ID)
                    page_num = int(match.group(1))
                    if 1 < page_num < 1000:  # Reasonable page range
                        return template
        
        return None
    
    async def scrape_thread(self, thread_url: str, max_pages: int = 100) -> Dict:
        self.thread_url = thread_url
        self._extract_thread_info(thread_url)
        domain = urlparse(thread_url).netloc
        cookies = self.cookie_extractor.get_cookies(domain)
        print(f"\n[+] Found {len(cookies)} cookies for {domain}")
        if self.thread_title:
            print(f"[+] Thread: {self.thread_title}")
        
        # Try gallery-dl first
        gallery_dl_urls = await self._try_gallery_dl(thread_url)
        for url in gallery_dl_urls:
            self.add_url(url)
        
        if gallery_dl_urls:
            print(f"[+] gallery-dl found {len(gallery_dl_urls)} URLs, skipping manual pagination")
        else:
            await self._scrape_pagination(thread_url, cookies, max_pages)
        
        # Extract post permalinks using Playwright if available
        if self.use_playwright:
            print("[+] Extracting post permalinks with Playwright...")
            post_urls = await self.extract_post_permalinks_playwright(thread_url, max_pages)
            for url in post_urls:
                self.add_url(url)
            print(f"[+] Found {len(post_urls)} post permalinks")
        else:
            print("[!] Post permalinks require JavaScript rendering. Install Playwright: pip install playwright && playwright install chromium")
        
        return self._generate_summary()
    
    async def _try_gallery_dl(self, url: str) -> List[str]:
        try:
            proc = await asyncio.create_subprocess_exec(
                "gallery-dl", "--cookies-from-browser", self.cookie_extractor.browser,
                "--get-urls", url,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
            )
            stdout, _ = await proc.communicate()
            if proc.returncode == 0:
                urls = [line.strip() for line in stdout.decode().splitlines() 
                       if line.strip() and not line.startswith("[")]
                print(f"[+] gallery-dl found {len(urls)} URLs")
                return urls
        except Exception:
            pass
        return []
    
    async def _scrape_pagination(self, thread_url: str, cookies: Dict[str, str], max_pages: int):
        base_url = thread_url.rstrip("/")
        
        # Load checkpoint
        start_page = self.load_checkpoint()
        if start_page > 0:
            start_page += 1  # Start from next page
        
        # First page: detect pagination pattern
        first_page_url = base_url
        if start_page <= 1:
            print("[+] Detecting pagination pattern...")
            try:
                html = await self.fetch_page_with_retry(first_page_url, cookies)
                pattern = self.detect_pagination_pattern(html, base_url)
                if pattern:
                    print(f"[+] Detected pagination pattern: {pattern}")
                else:
                    print("[+] No pagination pattern detected, using default /page-N")
            except Exception as e:
                print(f"[-] Error detecting pagination: {e}")
                pattern = None
        else:
            pattern = None
        
        # Determine URL generator
        def make_page_url(page: int) -> str:
            if pattern:
                if "{}" in pattern:
                    return urljoin(base_url + "/", pattern.format(page))
            # Default XenForo-style
            if page == 1:
                return base_url
            return f"{base_url}/page-{page}"
        
        pages_to_scrape = max_pages - start_page + 1
        if pages_to_scrape <= 0:
            return
        
        # Progress bar
        if HAS_TQDM:
            pbar = tqdm(total=pages_to_scrape, desc="Scraping pages", unit="page")
        else:
            pbar = tqdm(total=pages_to_scrape, desc="Scraping pages", unit="page")
        
        consecutive_empty = 0
        for i in range(pages_to_scrape):
            page = start_page + i
            page_url = make_page_url(page)
            
            pbar.set_description(f"Page {page} ({len(self.all_urls)} URLs)")
            
            try:
                html = await self.fetch_page_with_retry(page_url, cookies)
                links = self.extract_links(html, base_url)
                
                new_count = 0
                for link in links:
                    if link not in self.all_urls:
                        self.add_url(link)
                        new_count += 1
                
                pbar.set_postfix({"new": new_count, "total": len(self.all_urls)})
                
                if new_count == 0:
                    consecutive_empty += 1
                    if consecutive_empty >= 2:
                        print(f"\n[+] No new URLs for 2 consecutive pages, stopping")
                        break
                else:
                    consecutive_empty = 0
                
                # Save checkpoint every 5 pages
                if page % 5 == 0:
                    self.save_checkpoint(page)
                
            except Exception as e:
                print(f"\n[-] Error on page {page}: {e}")
                break
            
            pbar.update(1)
            await asyncio.sleep(self.request_delay)
        
        pbar.close()
        
        # Save final checkpoint
        self.save_checkpoint(start_page + pages_to_scrape - 1)
    
    def _generate_summary(self) -> Dict:
        return {
            "total": len(self.all_urls),
            "images": len(self.image_urls),
            "videos": len(self.video_urls),
            "posts": len(self.post_urls),
            "other": len(self.other_urls),
        }
    
    async def extract_post_permalinks_playwright(self, thread_url: str, max_pages: int = 100) -> List[str]:
        """Extract post permalinks using Playwright (requires JavaScript rendering)."""
        if not self.use_playwright:
            print("[!] Playwright not available. Install with: pip install playwright && playwright install chromium")
            return []
        
        post_urls = []
        base_url = thread_url.rstrip("/")
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                
                # Add cookies - handle both .domain and domain formats
                domain = urlparse(thread_url).netloc
                cookies = self.cookie_extractor.get_cookies(domain)
                if cookies:
                    cookie_list = []
                    for k, v in cookies.items():
                        cookie_list.append({"name": k, "value": v, "domain": domain, "path": "/"})
                        if not domain.startswith('.'):
                            cookie_list.append({"name": k, "value": v, "domain": "." + domain, "path": "/"})
                    await context.add_cookies(cookie_list)
                
                page = await context.new_page()
                
                for page_num in range(1, max_pages + 1):
                    page_url = f"{base_url}/page-{page_num}" if page_num > 1 else base_url
                    print(f"[+] Playwright: Loading page {page_num}...")
                    
                    try:
                        await page.goto(page_url, wait_until="networkidle", timeout=30000)
                        await page.wait_for_timeout(3000)
                        
                        # Check if we're logged in (XenForo sets data-logged-in attribute)
                        logged_in = await page.evaluate('() => document.documentElement.getAttribute("data-logged-in")')
                        if logged_in == "false":
                            print(f"[!] Page {page_num}: Not logged in (cookies may have expired).")
                            print(f"[!] Post permalinks require a valid forum session.")
                            print(f"[!] Please ensure you're logged into the forum in your browser, then re-run.")
                            break
                        
                        # Try multiple selectors for XenForo post permalinks
                        post_urls_page = await page.evaluate("""() => {
                            const urls = new Set();
                            
                            // Find all links with /post- in href
                            document.querySelectorAll('a[href*="/post-"]').forEach(a => {
                                if (a.href) urls.add(a.href);
                            });
                            
                            // XenForo 2.x message elements often have data attributes
                            document.querySelectorAll('.message, article.message, [data-content^="post-"]').forEach(el => {
                                const content = el.getAttribute('data-content');
                                if (content && content.startsWith('post-')) {
                                    const postId = content.replace('post-', '');
                                    const threadPath = window.location.pathname.split('/').slice(1,3).join('/');
                                    urls.add(window.location.origin + '/' + threadPath + '/post-' + postId);
                                }
                                const postId = el.getAttribute('data-post-id');
                                if (postId) {
                                    const threadPath = window.location.pathname.split('/').slice(1,3).join('/');
                                    urls.add(window.location.origin + '/' + threadPath + '/post-' + postId);
                                }
                            });
                            
                            // Also check for permalink anchors in message headers
                            document.querySelectorAll('.message-attribution a, .message-permalink a, .u-concealed[href*="/post-"]').forEach(a => {
                                if (a.href) urls.add(a.href);
                            });
                            
                            return Array.from(urls);
                        }""")
                        
                        for url in post_urls_page:
                            post_urls.append(url)
                        
                        print(f"[+] Page {page_num}: Found {len(post_urls_page)} post permalinks")
                        
                        # Check if we got new posts
                        if not post_urls_page:
                            print(f"[+] No more posts found on page {page_num}")
                            break
                            
                    except Exception as e:
                        print(f"[-] Playwright error on page {page_num}: {e}")
                        break
                
                await browser.close()
                
        except Exception as e:
            print(f"[-] Playwright extraction failed: {e}")
        
        return list(set(post_urls))  # Deduplicate
    
    def save_results(self, format: str = "txt"):
        prefix = self._get_output_prefix()
        
        files = {
            f"{prefix}_all.txt": sorted(self.all_urls),
            f"{prefix}_images.txt": self.image_urls,
            f"{prefix}_videos.txt": self.video_urls,
            f"{prefix}_posts.txt": self.post_urls,
            f"{prefix}_other.txt": self.other_urls,
        }
        for filename, urls in files.items():
            path = self.output_dir / filename
            with open(path, "w") as f:
                f.write("\n".join(urls))
            print(f"[+] Saved {len(urls)} URLs to {filename}")
        
        summary = self._generate_summary()
        summary["thread_url"] = self.thread_url
        summary["thread_title"] = self.thread_title
        summary["thread_id"] = self.thread_id
        summary["output_dir"] = str(self.output_dir)
        with open(self.output_dir / f"{prefix}_summary.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        if format == "json":
            for cat, urls in [("images", self.image_urls), ("videos", self.video_urls), ("posts", self.post_urls), ("other", self.other_urls)]:
                with open(self.output_dir / f"{prefix}_{cat}.json", "w") as f:
                    json.dump(urls, f, indent=2)


def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║         Interactive Forum Thread Scraper                      ║
║         Extracts images, videos, and links from threads       ║
╚══════════════════════════════════════════════════════════════╝
""")


def get_input(prompt: str, default: str = "", validator=None) -> str:
    while True:
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            if not user_input:
                return default
        else:
            user_input = input(f"{prompt}: ").strip()
            if not user_input:
                print("  This field is required.")
                continue
        if validator and not validator(user_input):
            print("  Invalid input. Please try again.")
            continue
        return user_input


def select_option(prompt: str, options: List[str], default_idx: int = 0) -> str:
    print(f"\n{prompt}")
    for i, opt in enumerate(options):
        marker = "→" if i == default_idx else " "
        print(f"  {marker} [{i+1}] {opt}")
    while True:
        choice = input(f"Select [1-{len(options)}] (default {default_idx+1}): ").strip()
        if not choice:
            return options[default_idx]
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx]
        except ValueError:
            pass
        print("  Invalid selection.")


def confirm(prompt: str, default: bool = True) -> bool:
    suffix = "Y/n" if default else "y/N"
    while True:
        choice = input(f"{prompt} [{suffix}]: ").strip().lower()
        if not choice:
            return default
        if choice in ("y", "yes"):
            return True
        if choice in ("n", "no"):
            return False
        print("  Please enter y or n.")


async def interactive_main():
    print_banner()
    
    # Step 1: Thread URL
    print("━" * 60)
    print("STEP 1: Thread URL")
    print("━" * 60)
    thread_url = get_input(
        "Enter the forum thread URL",
        validator=lambda x: x.startswith("http")
    )
    
    # Step 2: Browser selection
    print("\n━" * 60)
    print("STEP 2: Browser for Cookies")
    print("━" * 60)
    print("The scraper needs browser cookies for authenticated access.")
    print("Make sure you're logged into the forum in the selected browser.")
    browser = select_option(
        "Select browser:",
        ["firefox", "chrome", "chromium", "brave", "edge"],
        default_idx=0
    )
    
    # Step 3: Output directory
    print("\n━" * 60)
    print("STEP 3: Output Directory")
    print("━" * 60)
    default_out = "./scraped_output"
    output_dir = get_input("Output directory", default=default_out)
    output_path = Path(output_dir).expanduser().resolve()
    
    # Step 4: Options
    print("\n━" * 60)
    print("STEP 4: Options")
    print("━" * 60)
    max_pages = int(get_input("Max pages to scrape (0 = unlimited)", default="100"))
    if max_pages == 0:
        max_pages = 9999
    
    save_json = confirm("Also save as JSON?", default=False)
    
    # Step 5: Confirmation
    print("\n━" * 60)
    print("SUMMARY")
    print("━" * 60)
    print(f"  Thread URL:  {thread_url}")
    print(f"  Browser:     {browser}")
    print(f"  Output:      {output_path}")
    print(f"  Max pages:   {max_pages if max_pages < 9999 else 'unlimited'}")
    print(f"  Save JSON:   {'Yes' if save_json else 'No'}")
    
    if not confirm("\nStart scraping?", default=True):
        print("Cancelled.")
        return
    
    # Run scraper
    print("\n━" * 60)
    print("SCRAPING...")
    print("━" * 60)
    
    async with ThreadScraper(output_path, browser) as scraper:
        summary = await scraper.scrape_thread(thread_url, max_pages)
        scraper.save_results("json" if save_json else "txt")
        
        print("\n━" * 60)
        print("RESULTS")
        print("━" * 60)
        for k, v in summary.items():
            print(f"  {k.capitalize():8}: {v}")
        print(f"\nOutput saved to: {output_path}")
    
    # Post-scrape actions
    print("\n━" * 60)
    print("NEXT STEPS")
    print("━" * 60)
    actions = [
        "Open output directory",
        "View image URLs",
        "View video URLs",
        "View post URLs",
        "Run gallery-dl to download",
        "Scrape another thread",
        "Exit"
    ]
    
    while True:
        action = select_option("What would you like to do?", actions)
        
        if action == "Open output directory":
            os.system(f'xdg-open "{output_path}" 2>/dev/null || open "{output_path}" 2>/dev/null || explorer "{output_path}"')
        
        elif action == "View image URLs":
            prefix = scraper._get_output_prefix() if 'scraper' in dir() else ""
            img_files = list(output_path.glob("*_images.txt"))
            if not img_files:
                img_files = list(output_path.glob("image_urls.txt"))
            if img_files:
                img_file = img_files[0]
                count = len(open(img_file).readlines())
                print(f"\nFirst 20 of {count} image URLs:")
                for line in open(img_file).readlines()[:20]:
                    print(f"  {line.strip()}")
                if count > 20:
                    print(f"  ... and {count - 20} more")
        
        elif action == "View video URLs":
            vid_files = list(output_path.glob("*_videos.txt"))
            if not vid_files:
                vid_files = list(output_path.glob("video_urls.txt"))
            if vid_files:
                vid_file = vid_files[0]
                count = len(open(vid_file).readlines())
                print(f"\nFirst 20 of {count} video URLs:")
                for line in open(vid_file).readlines()[:20]:
                    print(f"  {line.strip()}")
                if count > 20:
                    print(f"  ... and {count - 20} more")
        
        elif action == "View post URLs":
            post_files = list(output_path.glob("*_posts.txt"))
            if not post_files:
                post_files = list(output_path.glob("post_urls.txt"))
            if post_files:
                post_file = post_files[0]
                count = len(open(post_file).readlines())
                print(f"\nFirst 20 of {count} post URLs:")
                for line in open(post_file).readlines()[:20]:
                    print(f"  {line.strip()}")
                if count > 20:
                    print(f"  ... and {count - 20} more")
        
        elif action == "Run gallery-dl to download":
            print("\nRunning gallery-dl on the thread...")
            os.system(f'gallery-dl --cookies-from-browser {browser} "{thread_url}"')
        
        elif action == "Scrape another thread":
            print("\n" + "=" * 60)
            await interactive_main()
            return
        
        elif action == "Exit":
            print("Goodbye!")
            break


def main():
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description="Forum thread scraper")
        parser.add_argument("thread_url", nargs="?", help="Thread URL")
        parser.add_argument("-o", "--output", default="./output")
        parser.add_argument("-b", "--browser", default="firefox")
        parser.add_argument("--max-pages", type=int, default=100)
        parser.add_argument("--json", action="store_true")
        parser.add_argument("-i", "--interactive", action="store_true")
        parser.add_argument("--playwright", action="store_true", help="Use Playwright for JavaScript rendering (post permalinks)")
        args = parser.parse_args()
        
        if args.interactive or not args.thread_url:
            asyncio.run(interactive_main())
        else:
            async def run_cli():
                async with ThreadScraper(args.output, args.browser, args.playwright) as scraper:
                    summary = await scraper.scrape_thread(args.thread_url, args.max_pages)
                    scraper.save_results("json" if args.json else "txt")
                    for k, v in summary.items():
                        print(f"  {k.capitalize()}: {v}")
            asyncio.run(run_cli())
    else:
        asyncio.run(interactive_main())


if __name__ == "__main__":
    main()