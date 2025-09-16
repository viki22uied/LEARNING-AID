import aiohttp
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.config import settings
from app.models.resources import Resource, ResourceCreate, LicenseInfo, SourceInfo, ContentInfo

logger = logging.getLogger(__name__)


class WikipediaHarvester:
    def __init__(self):
        self.api_base = settings.wikipedia_api_base
        self.session = None
        self.rate_limit_delay = 1.0  # 1 second between requests
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def search_articles(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search Wikipedia articles"""
        try:
            params = {
                "action": "opensearch",
                "search": query,
                "limit": limit,
                "format": "json",
                "namespace": 0  # Main namespace only
            }
            
            async with self.session.get(self.api_base, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                
                # Parse OpenSearch response format
                titles = data[1]
                descriptions = data[2]
                urls = data[3]
                
                articles = []
                for i, title in enumerate(titles):
                    articles.append({
                        "title": title,
                        "description": descriptions[i] if i < len(descriptions) else "",
                        "url": urls[i] if i < len(urls) else "",
                        "page_id": None  # Will be fetched separately
                    })
                
                return articles
        except Exception as e:
            logger.error(f"Error searching Wikipedia articles: {e}")
            return []
    
    async def get_article_content(self, title: str) -> Optional[Dict[str, Any]]:
        """Get full article content"""
        try:
            # First get page info
            params = {
                "action": "query",
                "titles": title,
                "prop": "extracts|info|pageprops",
                "explaintext": 1,
                "inprop": "url",
                "format": "json",
                "exintro": 1,  # Only introduction
                "exlimit": 1
            }
            
            async with self.session.get(self.api_base, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                
                pages = data["query"]["pages"]
                page_id = list(pages.keys())[0]
                page_data = pages[page_id]
                
                if page_id == "-1":  # Page not found
                    return None
                
                # Get full content
                full_params = {
                    "action": "query",
                    "titles": title,
                    "prop": "extracts",
                    "explaintext": 1,
                    "format": "json",
                    "exsectionformat": "plain"
                }
                
                await asyncio.sleep(self.rate_limit_delay)
                
                async with self.session.get(self.api_base, params=full_params) as response:
                    response.raise_for_status()
                    full_data = await response.json()
                    
                    full_pages = full_data["query"]["pages"]
                    full_page_data = full_pages[page_id]
                    
                    return {
                        "title": page_data["title"],
                        "page_id": page_id,
                        "url": page_data["fullurl"],
                        "extract": page_data.get("extract", ""),
                        "full_content": full_page_data.get("extract", ""),
                        "last_modified": page_data.get("touched", ""),
                        "length": page_data.get("length", 0)
                    }
        except Exception as e:
            logger.error(f"Error getting article content for {title}: {e}")
            return None
    
    async def get_category_articles(self, category: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get articles from a specific category"""
        try:
            params = {
                "action": "query",
                "list": "categorymembers",
                "cmtitle": f"Category:{category}",
                "cmlimit": limit,
                "format": "json"
            }
            
            async with self.session.get(self.api_base, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                
                members = data["query"]["categorymembers"]
                articles = []
                
                for member in members:
                    if member["ns"] == 0:  # Main namespace only
                        articles.append({
                            "title": member["title"],
                            "page_id": member["pageid"]
                        })
                
                return articles
        except Exception as e:
            logger.error(f"Error getting category articles for {category}: {e}")
            return []
    
    async def harvest_educational_content(self, topics: List[str], max_articles: int = 100) -> List[Resource]:
        """Harvest educational content from Wikipedia"""
        resources = []
        
        try:
            for topic in topics:
                logger.info(f"Harvesting content for topic: {topic}")
                
                # Search for articles
                articles = await self.search_articles(topic, limit=20)
                
                for article in articles[:max_articles // len(topics)]:
                    try:
                        # Get full content
                        content = await self.get_article_content(article["title"])
                        
                        if content and len(content["full_content"]) > 500:  # Minimum content length
                            resource = await self._create_resource_from_article(content)
                            resources.append(resource)
                        
                        await asyncio.sleep(self.rate_limit_delay)
                        
                    except Exception as e:
                        logger.error(f"Error processing article {article['title']}: {e}")
                        continue
                
                if len(resources) >= max_articles:
                    break
        
        except Exception as e:
            logger.error(f"Error in educational content harvest: {e}")
        
        logger.info(f"Harvested {len(resources)} resources from Wikipedia")
        return resources
    
    async def _create_resource_from_article(self, article_data: Dict[str, Any]) -> Resource:
        """Create a Resource object from Wikipedia article data"""
        # Extract key concepts from title and content
        title = article_data["title"]
        content = article_data["full_content"]
        
        # Simple tag extraction (in production, use NLP)
        words = title.lower().replace("_", " ").split()
        tags = [word for word in words if len(word) > 3]
        
        # Determine subject areas based on title
        subject_areas = self._extract_subject_areas(title, content)
        
        # Determine difficulty level
        difficulty = self._determine_difficulty(content)
        
        # Create license info (Wikipedia content is CC-BY-SA)
        license_info = LicenseInfo(
            type="CC-BY-SA-3.0",
            url="https://creativecommons.org/licenses/by-sa/3.0/",
            attribution_required=True,
            commercial_use_allowed=True,
            derivative_works_allowed=True
        )
        
        # Create source info
        source_info = SourceInfo(
            platform="Wikipedia",
            authors=[],  # Wikipedia articles have multiple contributors
            publication_date=datetime.utcnow(),
            last_updated=datetime.utcnow()
        )
        
        # Create content info
        content_info = ContentInfo(
            description=article_data.get("extract", "")[:500],
            tags=tags[:10],  # Limit tags
            subject_areas=subject_areas,
            difficulty_level=difficulty,
            language="en"
        )
        
        # Create resource
        resource = Resource(
            title=title,
            type="article",
            url=article_data["url"],
            downloadable=False,
            license=license_info,
            source=source_info,
            content=content_info
        )
        
        return resource
    
    def _extract_subject_areas(self, title: str, content: str) -> List[str]:
        """Extract subject areas from title and content"""
        subject_areas = []
        
        # Simple keyword-based extraction
        subject_keywords = {
            "mathematics": ["math", "mathematics", "algebra", "calculus", "geometry", "statistics"],
            "physics": ["physics", "mechanics", "thermodynamics", "quantum", "relativity"],
            "chemistry": ["chemistry", "organic", "inorganic", "biochemistry"],
            "biology": ["biology", "genetics", "evolution", "ecology", "microbiology"],
            "computer_science": ["computer", "programming", "algorithm", "software", "database"],
            "history": ["history", "historical", "ancient", "medieval", "modern"],
            "literature": ["literature", "poetry", "novel", "drama", "fiction"],
            "philosophy": ["philosophy", "ethics", "logic", "metaphysics", "epistemology"]
        }
        
        text = (title + " " + content[:1000]).lower()
        
        for subject, keywords in subject_keywords.items():
            if any(keyword in text for keyword in keywords):
                subject_areas.append(subject)
        
        return subject_areas[:3]  # Limit to 3 subject areas
    
    def _determine_difficulty(self, content: str) -> str:
        """Determine difficulty level based on content"""
        # Simple heuristic based on content length and complexity
        word_count = len(content.split())
        
        if word_count < 1000:
            return "beginner"
        elif word_count < 5000:
            return "intermediate"
        else:
            return "advanced"


# Global instance
wikipedia_harvester = WikipediaHarvester()
