
import json

ARTICLES_TO_REMOVE = (
    'Russia-Ukraine war: what we know on day',  # The Guardian
    'Russia-Ukraine war latest: what we know on day',  # The Guardian
    'Timeline: Week',  # Al Jazeera
    'Russia-Ukraine war: List of key events',  # Al Jazeera
    'Russia-Ukraine war: What happened today',  # NPR
    'Russia-Ukraine war: A weekly recap and look ahead',  # NPR
)

# Ref: https://github.com/dipanjanS/text-analytics-with-python/blob/master/New-Second-Edition/Ch05%20-%20Text%20Classification/contractions.py
with open('embed/config/contractions.json', 'r') as f:
    CONTRACTION_MAP = json.loads(f.read())