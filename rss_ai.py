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
        rss_urls: List[str],
        openai_api_key: str
    ) -> None:
        
        self.rss_urls = rss_urls
        self.openai_api_key = openai_api_key
        
        self.new_articles: List[Dict[str, str]] = []
        self.parser = RSSParser() # config here what should it parse
        self.llm = LLM() # config here
        self.feed = RSSFeed() # config here

    def run(self):
        
        for rss_url in self.rss_urls:
            
            parsed_feed = self.parser.parse_rss_feed(rss_url)
            
            title, desc = self.llm.rewrite_article(parsed_feed[0]["title"], parsed_feed[0]["description"])
            
            self.feed.update([{"title": title, "description": desc}])
            
            break
        
        print("Done")
        
        
    @classmethod
    def from_yaml(cls, path: str):
        with open(path, "r") as file:
            data = yaml.safe_load(file)

        return cls(**data)

if __name__ == "__main__":

    
    rss_ai = RSSAI.from_yaml("config.yml")
    # add error handling here
    
    
    rss_ai.run()