import feedparser
from bs4 import BeautifulSoup
from typing import Any, Dict, List


class RSSParser:
    
    def __init__(self) -> None:
        pass
    
    def parse_rss_feed(self, url: Any) -> List[Dict[str, str]]:
        
        parsed = feedparser.parse(url)
        
        articles = []
        
        for entry in parsed.entries:
            soup = BeautifulSoup(entry.description, "html.parser")
            description_text = soup.get_text()
            articles.append({"title": entry.title, "description": description_text})
        
        return articles