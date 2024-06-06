from typing import List
import feedparser
from bs4 import BeautifulSoup

class RSSParser:
    
    def __init__(self) -> None:
        pass
    
    def parse(self, url: str) -> List[dict]:
        """
        Returns all articles in a feed, with descriptions stripped to plain text if they contain HTML.
        """
        feed = feedparser.parse(url)
            
        for entry in feed.entries:
            soup = BeautifulSoup(entry.description, "html.parser")
            stripped_description = soup.get_text()
            entry.description = stripped_description
        
        return feed.entries