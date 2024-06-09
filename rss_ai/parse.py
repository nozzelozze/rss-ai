import hashlib
import json
import os
import pickle
from typing import List, Set
import feedparser
from bs4 import BeautifulSoup

PROCESSED_PATH = "processed.obj"

class RSSParser:
    
    def __init__(
        self, 
        grab_article_count: int,
        rss_urls: List[str],
    ) -> None:
        self.grab_article_count = grab_article_count
        self.rss_urls = rss_urls
        self.processed = self.load_processed()
        self.original_processed = self.load_processed()
        self.only_new = []
    
    def load_processed(self) -> List[str]:
        if os.path.exists(PROCESSED_PATH):
            with open(PROCESSED_PATH, "rb") as f:
                return pickle.load(f)
        return []
    
    def is_duplicate(self, entry) -> bool:
        return self.get_entry_id(entry) in self.original_processed
        
    def get_entry_id(self, entry) -> str:
        return hashlib.md5(str(entry["link"]).encode()).hexdigest()
    
    def get_articles_from_url(self, url: str):
        feed = feedparser.parse(url)
        
        sorted_entries = []
        
        if feed.entries == None:
            return []
        
        for entry in list(feed.entries)[:self.grab_article_count]:
            
            self.only_new.append(self.get_entry_id(entry))
            if self.is_duplicate(entry):
                continue
            
            if not "description" in entry:
                continue
            
            soup = BeautifulSoup(entry.description, "html.parser")
            stripped_description = soup.get_text()
            entry.description = stripped_description
            sorted_entries.append(entry)
            self.processed.append(self.get_entry_id(entry))
        
        return sorted_entries
    
    def clean_processes(self) -> None:
        cleaned = []
        for entry_id in self.processed:
            if not entry_id in self.only_new:
                continue
            cleaned.append(entry_id)
                
        with open(PROCESSED_PATH, "wb") as f:
            pickle.dump(cleaned, f)
            
    def clean_entry(self, entry) -> None:
        with open(PROCESSED_PATH, "wb") as f:
            pickle.dump([e for e in self.processed if e != self.get_entry_id(entry)], f)
            
    def get_entries(self) -> List[dict]:
        all_entries = []
        for rss_url in self.rss_urls:
            all_entries.extend(self.get_articles_from_url(rss_url))
        self.clean_processes()
        return all_entries