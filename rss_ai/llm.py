import base64
import ftplib
import io
from typing import List, Literal, Tuple
import uuid
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
        generate_image: bool,
        rewrite_title: bool,
        rewrite_body: bool,
        ftp
    ) -> None:
        self.client = OpenAI(api_key=openai_api_key)
        self.assistant_id_or_model = assistant_id_or_model
        self.model_prompts = model_prompts
        self.image_model = image_model
        self.image_prompt = image_prompt
        self.generate_image = generate_image
        self.image_size = image_size
        self.rewrite_title = rewrite_title
        self.rewrite_body = rewrite_body
        self.ftp = ftp
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
    
    def image(self, article):
        response = self.client.images.generate(
            model=self.image_model,
            prompt=f"{self.image_prompt}\n\n{article["title"]}\n{article["description"]}",
            size=self.image_size,
            quality="standard",
            n=1,
            response_format="b64_json"
        )

        image_data = base64.b64decode(response.data[0].b64_json)
        
        image_file = io.BytesIO(image_data)
        
        file_name = f"newsimage_{uuid.uuid4().hex}.jpg"
        with ftplib.FTP() as ftp:
            ftp.connect(self.ftp["server"], self.ftp["port"])
            ftp.login(self.ftp["user"], self.ftp["password"])
            ftp.cwd(self.ftp["virtual_images_path"])
            image_file.seek(0)
            ftp.storbinary(f'STOR {file_name}', image_file)

        article["GENERATED_IMAGE"] = self.ftp["images_url_directory"] + file_name
        
        return article
    
    def title_and_body(self, article):
        response: str
        if self.method == "assistant":
            
            return
        if self.method == "model":
            
            completion = self.client.chat.completions.create(
            model=self.assistant_id_or_model,
            messages=[
                {"role": "system", "content": self.model_prompts[0]},
                {"role": "user", "content": self.model_prompts[1] + f"\n\n{article["title"]}\n{article["description"]}"}
            ]
            )
            
            response = completion.choices[0].message.content
                        
        new_title, new_body =  self.parse_reponse(response)
        if self.rewrite_title:
            article["title"] = new_title

        if self.rewrite_body:
            article["description"] = new_body
            
        return article
    
    @logger.catch
    def rewrite(self, article):
        if self.rewrite_body or self.rewrite_title:
            article = self.title_and_body(article)
            
        if self.generate_image:
            article = self.image(article)
        
        return article