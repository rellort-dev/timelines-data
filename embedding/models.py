from datetime import datetime
from pydantic import BaseModel
from pydantic import HttpUrl

class Article(BaseModel):
    title: str
    url: HttpUrl
    thumbnailUrl: HttpUrl
    publishedTime: datetime
    description: str

class RawArticle(Article):
    content: str

class RawArticles(BaseModel):
    articles: list[RawArticle]

class ProcessedArticle(Article):
    embeddings: list[float]

class ProcessedArticles(BaseModel):
    articles: list[ProcessedArticle]