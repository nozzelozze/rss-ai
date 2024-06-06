from typing import Dict, List
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

class RSSFeed:
    
    def __init__(self) -> None:
        pass
    
    def update(self, articles: List[Dict[str, str]]):
        try:
            tree = ET.parse("aifeed.xml")
            root = tree.getroot()
            channel = root.find('channel')
        except FileNotFoundError:
            fg = FeedGenerator()
            fg.title("Hej")
            fg.link(href="https://computersweden.se")
            fg.description("Hej")
            fg.rss_file("aifeed.xml")
            tree = ET.parse("aifeed.xml")
            root = tree.getroot()
            channel = root.find('channel')

        for article in articles:
            item = ET.Element('item')
            title = ET.SubElement(item, 'title')
            title.text = article["title"]
            description = ET.SubElement(item, 'description')
            description.text = article["description"]
            pubDate = ET.SubElement(item, 'pubDate')
            pubDate.text = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S %z')
            channel.append(item)
        
        tree.write("aifeed.xml", encoding="utf-8", xml_declaration=True)
        
        ET.dump(root)
