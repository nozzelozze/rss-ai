import pickle
import pytz
import yaml
from typing import Dict, List
from rss_ai.llm import LLM
from rss_ai.parse import RSSParser
from rss_ai.feed import RSSFeed
from loguru import logger
from datetime import datetime

logger.remove(0)
logger.add(
    "logs/logfile_{time:YYYY-MM-DD}.log",
    level="INFO",
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    rotation="00:00",
    retention="1 month",
    compression="zip"
)

class RSSAI:
    
    def __init__(
        self, 
        LMMConfig,
        RSSParserConfig,
        RSSFeedConfig,
    ) -> None:
        self.new_articles: List[Dict[str, str]] = []
        self.parser = RSSParser(**RSSParserConfig)
        self.feed = RSSFeed(**RSSFeedConfig)
        self.llm = LLM(**LMMConfig)
    
    def run(self):
        logger.info("Starting run...")
        logger.info("Getting articles...")
        articles = self.parser.get_entries()
        logger.info("Rewriting articles...")
        original_articles = {}
        for article in articles:
            original_articles[article] = article.copy()
            rewritten_article = self.llm.rewrite(article)
            if rewritten_article == None:
                articles.remove(article)
                self.parser.clean_entry(original_articles[article])
                logger.error("recieved no rewritten article, skipping")
                continue
                
            logger.info(f"article with title '{article["title"]}' rewritten")
        
        self.feed.update(articles)
        
        logger.info("Updating RSS feed...")
        now = datetime.now(tz=pytz.timezone("Europe/Stockholm")).strftime("%d/%m/%Y, %H:%M:%S")
        logger.info(f"Run done at {now}")
        open("latestrun.txt", "w").write(now)
        
    @classmethod
    def from_yaml(cls, path: str):
        with open(path, "r") as file:
            data = yaml.safe_load(file)

        return cls(**data)

if __name__ == "__main__":
    rss_ai = RSSAI.from_yaml("config.yml")
    rss_ai.run()