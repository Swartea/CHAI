"""Fanqie novel (番茄小说) hot list crawler.

Crawls fanqienovel.com to fetch hot list entries and popular books
for book deconstruction analysis.
"""

import asyncio
import json
import re
from dataclasses import dataclass, field
from typing import Optional

import httpx
from bs4 import BeautifulSoup


BASE_URL = "https://fanqienovel.com"
API_BASE = "https://fanqienovel.com/api/reader"


@dataclass
class FanqieHotEntry:
    """A hot list entry/topic from Fanqie novel."""
    id: str
    name: str
    category: str
    book_count: int = 0
    description: str = ""


@dataclass
class FanqieBook:
    """A book from Fanqie novel platform."""
    id: str
    title: str
    author: str
    genre: str
    synopsis: str = ""
    word_count: int = 0
    rating: float = 0.0
    tags: list[str] = field(default_factory=list)
    cover_url: str = ""


class FanqieCrawler:
    """Crawler for Fanqie novel hot list and book data."""

    def __init__(
        self,
        timeout: int = 30,
        max_retries: int = 3,
        user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ):
        """Initialize the crawler.

        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts for failed requests
            user_agent: User agent string for requests
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.user_agent = user_agent
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                headers={"User-Agent": self.user_agent},
                follow_redirects=True,
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def _request_with_retry(self, url: str, **kwargs) -> httpx.Response:
        """Make HTTP request with retry logic."""
        client = await self._get_client()
        for attempt in range(self.max_retries):
            try:
                response = await client.get(url, **kwargs)
                response.raise_for_status()
                return response
            except (httpx.TimeoutException, httpx.HTTPStatusError) as e:
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(1 * (attempt + 1))
        raise RuntimeError("Should not reach here")

    async def get_hot_list(self, limit: int = 20) -> list[FanqieHotEntry]:
        """Fetch the Fanqie hot list entries.

        Args:
            limit: Maximum number of entries to fetch

        Returns:
            List of hot list entries
        """
        # Fanqie uses an API endpoint for hot list
        # Try API first, fall back to web scraping
        try:
            return await self._get_hot_list_api(limit)
        except Exception:
            return await self._get_hot_list_web(limit)

    async def _get_hot_list_api(self, limit: int) -> list[FanqieHotEntry]:
        """Fetch hot list via API."""
        url = f"{API_BASE}/auction-rank/hot-list"
        response = await self._request_with_retry(url)
        data = response.json()

        entries = []
        items = data.get("data", {}).get("list", []) if isinstance(data, dict) else []

        for item in items[:limit]:
            entry = FanqieHotEntry(
                id=str(item.get("id", "")),
                name=item.get("title", item.get("name", "")),
                category=item.get("category", ""),
                book_count=item.get("book_count", 0),
                description=item.get("description", ""),
            )
            entries.append(entry)

        return entries

    async def _get_hot_list_web(self, limit: int) -> list[FanqieHotEntry]:
        """Fetch hot list by scraping the web page."""
        response = await self._request_with_retry(f"{BASE_URL}/")
        soup = BeautifulSoup(response.text, "html.parser")

        entries = []
        # Hot list entries are typically in specific page sections
        # Try to find rank/list items
        rank_items = soup.select(".rank-item, .hot-item, [class*='rank'], [class*='hot']")

        for item in rank_items[:limit]:
            link = item.select_one("a")
            if link:
                name = link.get_text(strip=True)
                href = link.get("href", "")
                entry_id = re.search(r"/(\d+)", href)
                entries.append(
                    FanqieHotEntry(
                        id=entry_id.group(1) if entry_id else href,
                        name=name,
                        category="",
                    )
                )

        return entries

    async def get_books_by_entry(self, entry_id: str, limit: int = 10) -> list[FanqieBook]:
        """Fetch popular books under a specific hot list entry.

        Args:
            entry_id: The hot list entry ID
            limit: Maximum number of books to fetch

        Returns:
            List of books
        """
        try:
            return await self._get_books_by_entry_api(entry_id, limit)
        except Exception:
            return await self._get_books_by_entry_web(entry_id, limit)

    async def _get_books_by_entry_api(self, entry_id: str, limit: int) -> list[FanqieBook]:
        """Fetch books via API."""
        url = f"{API_BASE}/auction-rank/entry/books"
        params = {"entry_id": entry_id, "limit": limit}
        response = await self._request_with_retry(url, params=params)
        data = response.json()

        books = []
        items = data.get("data", {}).get("list", []) if isinstance(data, dict) else []

        for item in items[:limit]:
            book = FanqieBook(
                id=str(item.get("book_id", item.get("id", ""))),
                title=item.get("title", ""),
                author=item.get("author", ""),
                genre=item.get("genre", item.get("category", "")),
                synopsis=item.get("synopsis", item.get("description", "")),
                word_count=item.get("word_count", 0),
                rating=item.get("rating", 0.0),
                tags=item.get("tags", []),
                cover_url=item.get("cover_url", ""),
            )
            books.append(book)

        return books

    async def _get_books_by_entry_web(self, entry_id: str, limit: int) -> list[FanqieBook]:
        """Fetch books by scraping web page."""
        url = f"{BASE_URL}/entry/{entry_id}"
        response = await self._request_with_retry(url)
        soup = BeautifulSoup(response.text, "html.parser")

        books = []
        book_items = soup.select(".book-item, .novel-item, [class*='book'], [class*='novel']")

        for item in book_items[:limit]:
            title_elem = item.select_one(".title, .book-title, h3, h4")
            author_elem = item.select_one(".author, .writer")
            desc_elem = item.select_one(".desc, .synopsis, .description")

            title = title_elem.get_text(strip=True) if title_elem else ""
            author = author_elem.get_text(strip=True) if author_elem else ""
            desc = desc_elem.get_text(strip=True) if desc_elem else ""

            link = item.select_one("a")
            href = link.get("href", "") if link else ""
            book_id = re.search(r"/book/(\d+)", href)
            book_id_str = book_id.group(1) if book_id else href

            if title:
                books.append(
                    FanqieBook(
                        id=book_id_str,
                        title=title,
                        author=author,
                        genre="",
                        synopsis=desc,
                    )
                )

        return books

    async def get_book_detail(self, book_id: str) -> Optional[FanqieBook]:
        """Fetch detailed information about a specific book.

        Args:
            book_id: The book ID

        Returns:
            Book details or None if not found
        """
        try:
            url = f"{API_BASE}/book/detail"
            params = {"book_id": book_id}
            response = await self._request_with_retry(url, params=params)
            data = response.json()

            item = data.get("data", {}) if isinstance(data, dict) else {}
            if not item:
                return None

            return FanqieBook(
                id=str(item.get("book_id", book_id)),
                title=item.get("title", ""),
                author=item.get("author", ""),
                genre=item.get("genre", item.get("category", "")),
                synopsis=item.get("synopsis", item.get("description", "")),
                word_count=item.get("word_count", 0),
                rating=item.get("rating", 0.0),
                tags=item.get("tags", []),
                cover_url=item.get("cover_url", ""),
            )
        except Exception:
            return None

    async def get_book_chapters(self, book_id: str, limit: int = 20) -> list[dict]:
        """Fetch chapter list for a book (for deconstruction analysis).

        Args:
            book_id: The book ID
            limit: Maximum number of chapters to fetch

        Returns:
            List of chapter info dicts
        """
        try:
            url = f"{API_BASE}/book/chapters"
            params = {"book_id": book_id, "limit": limit}
            response = await self._request_with_retry(url, params=params)
            data = response.json()

            if isinstance(data, dict):
                return data.get("data", {}).get("chapters", [])
            return []
        except Exception:
            return []

    async def get_popular_books(self, genre: str = "", limit: int = 20) -> list[FanqieBook]:
        """Fetch popular books, optionally filtered by genre.

        Args:
            genre: Genre filter (empty for all)
            limit: Maximum number of books to fetch

        Returns:
            List of popular books
        """
        try:
            url = f"{API_BASE}/book/popular"
            params = {"limit": limit}
            if genre:
                params["genre"] = genre
            response = await self._request_with_retry(url, params=params)
            data = response.json()

            books = []
            items = data.get("data", {}).get("list", []) if isinstance(data, dict) else []

            for item in items[:limit]:
                books.append(
                    FanqieBook(
                        id=str(item.get("book_id", item.get("id", ""))),
                        title=item.get("title", ""),
                        author=item.get("author", ""),
                        genre=item.get("genre", item.get("category", "")),
                        synopsis=item.get("synopsis", ""),
                        word_count=item.get("word_count", 0),
                        rating=item.get("rating", 0.0),
                        tags=item.get("tags", []),
                        cover_url=item.get("cover_url", ""),
                    )
                )
            return books
        except Exception:
            return []

    async def __aenter__(self) -> "FanqieCrawler":
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args) -> None:
        """Async context manager exit."""
        await self.close()


async def demo_crawl_hot_list() -> None:
    """Demo: crawl the Fanqie hot list and print results."""
    async with FanqieCrawler() as crawler:
        print("Fetching Fanqie hot list...")
        entries = await crawler.get_hot_list(limit=10)
        print(f"Found {len(entries)} hot list entries:")
        for entry in entries:
            print(f"  [{entry.id}] {entry.name} ({entry.category}) - {entry.book_count} books")
