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
        for article in articles:
            """             response = self.llm.rewrite(article.title, article.description)
            if response == None:
                articles.remove(article)
                logger.error("recieved no rewritten article, skipping")
                continue
            new_title, new_description = response
            if self.rewrite_title:
                article["title"] = new_title

            if self.rewrite_description:
                article["description"] = new_description """
            
            article["description"] = "YEP!"
        logger.info("Updating RSS feed...")
        self.feed.update(articles)
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