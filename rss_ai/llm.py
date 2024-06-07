from typing import List, Literal, Tuple
from openai import OpenAI
from loguru import logger

class LLM:
    
    def __init__(self, 
        openai_api_key: str, 
        assistant_id_or_model: str, 
        model_prompts: List[str], 
        image_model: str,
        image_prompt: str,
        image_size: str,
        generate_image: bool
    ) -> None:
        self.client = OpenAI(api_key=openai_api_key)
        self.assistant_id_or_model = assistant_id_or_model
        self.model_prompts = model_prompts
        self.image_model = image_model
        self.image_prompt = image_prompt
        self.generate_image = generate_image
        self.image_size = image_size
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
        
        logger.error(f"assistant_id_or_model {self.assistant_id_or_model} is neither an assistant or openai model")
    
    def parse_reponse(self, message: str) -> Tuple[str, str]:
        title, text = message.split('\n\n', 1)
        return title, text
    
    def image(self, article_title, article_text) -> str:
        """
        Returns URL ( expires after one hour )
        """
        if not self.generate_image:
            return None
        
        response = self.client.images.generate(
            model=self.image_model,
            prompt=f"{self.image_prompt}\n\n{article_title}\n{article_text}",
            size=self.image_size,
            quality="standard",
            n=1,
        )

        image_url = response.data[0].url
        return image_url
    
    @logger.catch
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
        
        return None