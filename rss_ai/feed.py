import feedparser
import os
import pickle
from typing import List
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
from pathlib import Path
import pytz

class RSSFeed:
    
    def __init__(self, file_name: str, max_articles: int, rss_config: dict) -> None:
        self.file_name = file_name
        self.max_articles = max_articles
        self.rss_config = rss_config
    
    def get_generator(self) -> FeedGenerator:
        fg = FeedGenerator()
        fg.title(self.rss_config["title"])
        fg.link(href=self.rss_config["link"])
        fg.description(self.rss_config["description"])
        fg.language(self.rss_config["language"])
        return fg
    
    def update(self, articles: List[dict]):
        """
        Updates the RSS feed.
        Args:
            articles (List[dict]): The articles that should be added to the RSS feed.
        """
        fg = self.get_generator()
        if os.path.exists("feed.obj"):
            with open("feed.obj", "rb") as f:
                fg = pickle.load(f)

        existing_entries = list(feedparser.parse(fg.rss_str()).entries)

        for article in articles:
            fe = fg.add_entry()
            fe.title(article["title"])
            fe.description(article["description"])
            fe.pubDate(datetime.now(tz=pytz.timezone("Europe/Stockholm")))

        all_entries = existing_entries + list(feedparser.parse(fg.rss_str()).entries)
        all_entries.sort(key=lambda x: x["published"], reverse=True)

        fg = self.get_generator()
        for entry in all_entries[:self.max_articles]:
            fe = fg.add_entry()
            fe.title(entry.title)
            fe.description(entry.description)
            fe.pubDate(entry.published)

        rss_feed = fg.rss_str(pretty=True)
        rss_feed = rss_feed.decode("utf-8")

        with open(self.file_name, "w", encoding="utf-8") as f:
            f.write(rss_feed)

        with open("feed.obj", "wb") as f:
            pickle.dump(fg, f)