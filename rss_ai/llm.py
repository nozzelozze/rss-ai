import json
from typing import Tuple
import requests

class LLMHandler:
    pass

class LLM:
    
    # add configs here etc
    
    def __init__(self) -> None:
        pass
    
    def rewrite_article(self, title: str, description: str) -> Tuple[str, str]:
        
        payload = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Summarize this article to five short Swedish sentences:\n\n{description}"}
            ]
        }

        res = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer ",
                "Content-Type": "application/json"
            },
            data=json.dumps(payload)
        )
        
        result = res.json()
        
        completion_message = result['choices'][0]['message']['content']
        
        return "title", completion_message