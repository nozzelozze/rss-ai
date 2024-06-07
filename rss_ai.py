import yaml
from dataclasses import dataclass
from typing import Dict, List, Sequence
from rss_ai.llm import LLM
from rss_ai.parse import RSSParser
from rss_ai.feed import RSSFeed
from loguru import logger

logger.remove(0)
logger.add(
    "logfile_{time:YYYY-MM-DD}.log",
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
        articles = self.parser.get_articles()
        for article in articles:
            """
            new_title, new_description = self.llm.rewrite(article.title, article.description)
            if self.rewrite_title:
                article["title"] = new_title

            if self.rewrite_description:
                article["description"] = new_description
            """
            
            article["description"] = "YEP!"
        self.feed.update(articles)
        
    @classmethod
    def from_yaml(cls, path: str):
        with open(path, "r") as file:
            data = yaml.safe_load(file)

        return cls(**data)

if __name__ == "__main__":

    
    rss_ai = RSSAI.from_yaml("config.yml")
    # add error handling here
    
    
    rss_ai.run()