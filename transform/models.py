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

class TransformedArticle(Article):
    embeddings: list[float]

class TransformedArticles(BaseModel):
    articles: list[TransformedArticle]