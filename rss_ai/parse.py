import hashlib
import json
import os
import pickle
from typing import List, Set
import feedparser
from bs4 import BeautifulSoup

class RSSParser:
    
    def __init__(
        self, 
        grab_article_count: int,
        rss_urls: List[str],
        rewrite_title: bool,
        rewrite_description: bool,
    ) -> None:
        self.grab_article_count = grab_article_count
        self.rss_urls = rss_urls
        self.rewrite_title = rewrite_title
        self.rewrite_description = rewrite_description
        self.processed = self.load_processed()
    
    def load_processed(self) -> Set[str]:
        if os.path.exists("processed.obj"):
            with open("processed.obj", "rb") as f:
                return pickle.load(f)
        return set()
    
    def is_duplicate(self, entry: dict) -> bool:
        return self.get_entry_id(entry) in self.processed
        
    def get_entry_id(self, entry: dict) -> str:
        return hashlib.md5(json.dumps(entry, sort_keys=True).encode()).hexdigest()
    
    def process_entry(self, entry: dict) -> None:
        self.processed.add(self.get_entry_id(entry))
        with open("processed.obj", "wb") as f:
            pickle.dump(self.processed, f)
    
    def get_articles_from_url(self, url: str):
        feed = feedparser.parse(url)
        
        sorted_entries = []
        
        if feed.entries == None:
            return []
        
        for entry in list(feed.entries)[:self.grab_article_count]:
            
            if self.is_duplicate(entry):
                continue
            
            soup = BeautifulSoup(entry.description, "html.parser")
            stripped_description = soup.get_text()
            entry.description = stripped_description
            sorted_entries.append(entry)
            self.process_entry(entry)
        
        return sorted_entries
    
    def get_articles(self) -> List[dict]:
        all_articles = []
        for rss_url in self.rss_urls:
            all_articles.extend(self.get_articles_from_url(rss_url))
        return all_articles