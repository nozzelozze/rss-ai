import json
from typing import List, Literal, Tuple
import requests
from openai import OpenAI
class LLM:
    
    def __init__(self, openai_api_key: str, assistant_id_or_model: str, model_prompts: List[str]) -> None:
        self.client = OpenAI(api_key=openai_api_key)
        self.assistant_id_or_model = assistant_id_or_model
        self.model_prompts = model_prompts
        self.method: Literal["assistant", "model"] = None
        self.setup_service()
    
    def setup_service(self):
        models = self.client.models.list()
        if self.assistant_id_or_model in map(lambda m: m.id, models.data):
            self.method = "model"
            return
        
        assistants = self.client.beta.assistants.list()
        if self.assistant_id_or_model in map(lambda a: a.id, assistants.data):
            self.method = "assistant"
            return
        
        # handle error here
    
    def parse_reponse(self, message: str) -> Tuple[str, str]:
        title, text = message.split('\n\n', 1)
        return title, text
        
    def rewrite(self, title: str, text: str) -> Tuple[str, str]:
           
        if self.method == "assistant":
            
            return
        
        if self.method == "model":
            
            completion = self.client.chat.completions.create(
            model=self.assistant_id_or_model,
            messages=[
                {"role": "system", "content": self.model_prompts[0]},
                {"role": "user", "content": self.model_prompts[1] + f"\n\n{title}\n{text}"}
            ]
            )
                        
            return self.parse_reponse(completion.choices[0].message.content)
        
        # handle error
        
        return "title", "completion_message"