
import functools
import re
import spacy
from embed.config import config

# Prevents the model from being loaded from importing the module
@functools.cache
def get_nlp():
    return spacy.load('en_core_web_lg', 
                 exclude=['ner', 'tok2vec', 'tagger', 'parser', 'senter', 
                          'textcat', 'attribute_ruler', 'lemmatizer'])

def process_text_for_nlp(text: str) -> str:
    # Convert words into lower case
    text = text.lower()
    
    # Convert contractions into formal form
    for contraction, formal_form in config.CONTRACTION_MAP.items():
        text = text.replace(contraction, formal_form)

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
    
    # Remove non-alphanumeric characters
    text = re.sub('[^a-zA-Z0-9]', ' ', text)
    
    # Remove duplicate spaces
    text = re.sub(' +', ' ', text)
    
    # Remove trailing and leading spaces 
    text = text.strip()
    
    return text
    
def embed_text(text) -> list[float]:
    doc = get_nlp()(text)
    embeddings = doc.vector
    # Convert from np array to list, and from np float to python float
    # to comply with pydantic type checking.
    embeddings = list(embeddings.astype(float))
    return embeddings

def is_problematic_article(article):
    if "title" not in article:
        return True
    return article["title"].startswith(tuple(config.ARTICLES_TO_REMOVE))