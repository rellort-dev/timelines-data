from datetime import datetime
from pydantic import BaseModel
from pydantic import HttpUrl

class Article(BaseModel):
    title: str
    url: HttpUrl
    source: str
    thumbnailUrl: HttpUrl
    publishedTime: datetime
    description: str
    content: str

class Articles(BaseModel):
    articles: list[Article]

class ProcessedArticle(Article):
    embeddings: list[float]

class ProcessedArticles(BaseModel):
    articles: list[ProcessedArticle]