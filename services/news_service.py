"""
News Service for fetching top news stories
"""
from typing import List, Dict, Any
from config import settings
import logging
import httpx

logger = logging.getLogger(__name__)


class NewsService:
    """Service for fetching news from NewsAPI or similar services"""

    def __init__(self):
        self.api_key = settings.NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2"

    @staticmethod
    def is_configured() -> bool:
        """Check if the service is properly configured"""
        return bool(settings.NEWS_API_KEY)

    async def fetch_top_stories(self, max_results: int = None) -> List[Dict[str, Any]]:
        """
        Fetch top news stories

        Args:
            max_results: Maximum number of articles to fetch

        Returns:
            List of news article dictionaries
        """

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/top-headlines",
                    params={
                        "apiKey": self.api_key,
                        "country": "us",
                        "pageSize": max_results or settings.MAX_NEWS_ARTICLES
                    },
                    timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()
                    articles = data.get('articles', [])

                    return [
                        {
                            "title": article.get("title"),
                            "source": article.get("source", {}).get("name"),
                            "description": article.get("description"),
                            "url": article.get("url"),
                            "publishedAt": article.get("publishedAt")
                        }
                        for article in articles
                    ]
                else:
                    logger.error(f"News API error: {response.status_code}")
                    return []

        except Exception as e:
            logger.error(f"Error fetching news: {str(e)}")
            return []
