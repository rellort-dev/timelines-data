
import re
import gc
from transform.config import config
from transform.models import Article
import torch
import sentence_transformers


def process_text_for_nlp(text: str) -> str:
    # Remove HTML tags
    text = re.sub(r'<[^<>]*>', '', text)
    
    # Remove everything in parenthesis
    text = re.sub(r'\([^\(\)]*\)', '', text)
    text = re.sub(r'\[[^\[\]]*\]', '', text)

    # Remove words or phrases that convey no meaning    
    news_agencies = ['cnbc', 'the washington post', 'the associated press', 'reuters.com',
                    'reuters', 'read more at straitstimes.com.', 'bbc news']
    boilerplate_text = ['placeholder while article actions load', 'posted',  
                        'image source',  'getty images', 'image caption',  'good morning and welcome to the climate 202']
    for meaningless_string in (news_agencies + boilerplate_text):
        text = text.replace(meaningless_string, '')
    
    # Remove trailing and leading spaces 
    text = text.strip()
    
    return text


device = "cuda" if torch.cuda.is_available() else "cpu"
sent_transformer = sentence_transformers.SentenceTransformer('all-MiniLM-L6-v2', device=device)
sent_transformer.max_seq_length = 512
def embed_article(article: dict) -> list[float]:
    title_list = [article["title"] + article["description"]]
    body_list = [article["content"]]
    title_embeddings = sent_transformer.encode(title_list)
    body_embeddings = sent_transformer.encode(body_list)
    embeddings = (0.6 * title_embeddings) + (0.4 * body_embeddings)

    torch.cuda.empty_cache()
    gc.collect()

    return list(embeddings[0])


def is_problematic_article(article: Article) -> bool:
    if "title" not in article:
        raise AssertionError("Article object does not contain title")
    return article["title"].startswith(tuple(config.ARTICLES_TO_REMOVE))