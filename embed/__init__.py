
import copy
import spacy
import pandas as pd
from embed.config import config
from embed.models import ProcessedArticles, RawArticles

nlp = spacy.load('en_core_web_lg', 
                 exclude=['ner', 'tok2vec', 'tagger', 'parser', 'senter', 
                          'textcat', 'attribute_ruler', 'lemmatizer'])

def remove_problematic_articles(df, columns_to_check: list[str]):
    df = copy.deepcopy(df)
    
    for column in columns_to_check:
        if column not in df:
            raise Exception(f"Column to check '{column}' does not exist in the DataFrame.")
    
    for column in columns_to_check:
        df = df.drop_duplicates(subset=[column])
        df = df.dropna(subset=[column])
    
    if "title" not in columns_to_check:
        return df
    
    # Remove s that do not encapsulate one and only one event
    # (e.g. The Guardian's daily 'what we know on day x of the ukraine war' article series)
    mask = df.title.str.startswith(config.ARTICLES_TO_REMOVE)
    df = df[~mask] 
        
    return df

def process_text_columns_for_displaying(df, input_columns: list[str]):
    return df

def process_text_columns_for_nlp(df, input_columns: list[str]):
    df = copy.deepcopy(df)

    for column in input_columns:
        # Convert words into lower case
        df[column] = df[column].str.lower()
        
        # Convert contractions into formal form
        df[column] = df[column].replace(config.CONTRACTION_MAP, regex=True)

        # Remove HTML tags
        df[column] = df[column].str.replace(r'<[^<>]*>', '', regex=True)
        
        # Remove everything in parenthesis
        df[column] = df[column].str.replace(r'\([^\(\)]*\)', '', regex=True)
        df[column] = df[column].str.replace(r'\[[^\[\]]*\]', '', regex=True)

        # Remove words or phrases that convey no meaning    
        news_agencies = ['cnbc', 'the washington post', 'the associated press', 'reuters.com',
                        'reuters', 'read more at straitstimes.com.', 'bbc news']
        boilerplate_text = ['placeholder while article actions load', 'posted',  
                            'image source',  'getty images', 'image caption',  'good morning and welcome to the climate 202']
        for meaningless_string in (news_agencies + boilerplate_text):
            df[column] = df[column].str.replace(meaningless_string, '', regex=True)
        
        # Remove non-alphanumeric characters
        df[column] = df[column].str.replace('[^a-zA-Z0-9]', ' ', regex=True)
        
        # Remove duplicate spaces
        df[column] = df[column].str.replace(' +', ' ', regex=True)
        
        # Remove trailing and leading spaces 
        df[column] = df[column].str.strip()
    
    return df

def embed_column(df, input_column: str,  output_column: str):
    df = copy.deepcopy(df)
    docs = list(nlp.pipe(df[input_column]))
    embeddings = [doc.vector for doc in docs]
    # Convert from np array to list, and from np float to python float
    # to comply with pydantic type checking.
    embeddings = [list(vector.astype(float)) for vector in embeddings]
    df[output_column] = embeddings
    return df

