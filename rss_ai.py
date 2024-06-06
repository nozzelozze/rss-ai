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
        openai_api_key: str,
        assistant_id_or_model: str,
        model_prompts: List[str],
        rewrite_title: bool,
        rewrite_description: bool,
        rss_file_name: str,
        max_articles: int,
        rss: dict
    ) -> None:
        
        self.rss_urls = rss_urls
        self.openai_api_key = openai_api_key
        
        self.rewrite_title = rewrite_title
        self.rewrite_description = rewrite_description
        self.new_articles: List[Dict[str, str]] = []
        self.parser = RSSParser()
        self.feed = RSSFeed(rss_file_name, max_articles, rss)
        self.llm = LLM(openai_api_key, assistant_id_or_model, model_prompts)
    
    def run(self):
        for rss_url in self.rss_urls:
            articles = self.parser.parse(rss_url)
            
            for article in articles:
                new_title, new_description = self.llm.rewrite(article.title, article.description)
                if self.rewrite_title:
                    article["title"] = new_title

                if self.rewrite_description:
                    article["description"] = new_description

                break # break for now
            
            self.feed.update(articles[:1])
            
            break # break for now
        
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