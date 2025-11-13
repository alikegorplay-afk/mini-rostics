import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")
    AUTH_TOKEN: str = os.getenv("AUTH_TOKEN")
    PATH_TO_SAVE_IMAGE: Path = Path("data")
    
    def __init__(self):
        for k, v in self.__annotations__.items():
            if not isinstance(self.__getattribute__(k), v):
                raise TypeError("Один из обязательных атрибутов пуст")
            
    @property
    def img_404(self):
        return self.PATH_TO_SAVE_IMAGE / '404.jpg'


config = Config()