import feedparser
import os
import pickle
from typing import List
from feedgen.feed import FeedGenerator
from datetime import datetime
from loguru import logger
import pytz

FEED_PATH = "pickles/feed.obj"

class RSSFeed:
    
    def __init__(self, file_name: str, path_to_file: str, max_articles: int, info: dict) -> None:
        self.file_name = file_name
        self.max_articles = max_articles
        self.info = info
        self.path_to_file = path_to_file
    
    def get_generator(self) -> FeedGenerator:
        fg = FeedGenerator()
        fg.title(self.info["title"])
        fg.link(href=self.info["link"])
        fg.description(self.info["description"])
        fg.language(self.info["language"])
        return fg

    def update(self, articles: List[dict]):
        """
        Updates the RSS feed.
        Args:
            articles (List[dict]): The articles that should be added to the RSS feed.
        """
        fg = self.get_generator()
        if os.path.exists(FEED_PATH):
            with open(FEED_PATH, "rb") as f:
                fg = pickle.load(f)

        existing_entries = list(feedparser.parse(fg.rss_str()).entries)
        existing_entries.reverse()

        temp_fg = self.get_generator()
        for article in articles:
            fe = temp_fg.add_entry()
            fe.title(article["title"])
            fe.description(article["description"])
            fe.category({"term": article["OWN_CATEGORY"]})
            fe.pubDate(datetime.now(tz=pytz.timezone("Europe/Stockholm")))
            if "GENERATED_IMAGE" in article and article["GENERATED_IMAGE"] is not None:
                fe.enclosure(article["GENERATED_IMAGE"], 0, "image/jpeg")

        all_entries = existing_entries + list(feedparser.parse(temp_fg.rss_str()).entries) 
        
        final_fg = self.get_generator()
        for entry in all_entries[-self.max_articles:]:
            fe = final_fg.add_entry()
            fe.title(entry.title)
            fe.description(entry.description)
            fe.pubDate(entry.published)
            fe.category({"term": entry.category})
            if "links" in entry:
                for link in entry.links:
                    if link.rel == "enclosure":
                        fe.enclosure(link.href, 0, "image/jpeg")
                
        rss_feed = final_fg.rss_str(pretty=True)
        rss_feed = rss_feed.decode("utf-8")

        for entry in all_entries:
            if hasattr(entry, "links"):
                for link in entry.links:
                    if link.rel == "enclosure":
                        img_tag = f'<![CDATA[<img src="{link.href}" alt="{entry.title}"><br>{entry.description}]]>'
                        rss_feed = rss_feed.replace(entry.description, img_tag)

        with open(self.path_to_file + self.file_name, "w", encoding="utf-8") as f:
            f.write(rss_feed)

        with open(FEED_PATH, "wb") as f:
            pickle.dump(final_fg, f)