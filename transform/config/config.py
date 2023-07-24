
import json

ARTICLES_TO_REMOVE = (
    'Russia-Ukraine war: what we know on day',  # The Guardian
    'Russia-Ukraine war latest: what we know on day',  # The Guardian
    'Timeline: Week',  # Al Jazeera
    'Russia-Ukraine war: List of key events',  # Al Jazeera
    'Russia-Ukraine war: What happened today',  # NPR
    'Russia-Ukraine war: A weekly recap and look ahead',  # NPR
    'Your Monday Briefing',  # NYTimes
    'Your Tuesday Briefing',
    'Your Wednesday Briefing',
    'Your Thursday Briefing',
    'Your Friday Briefing',
    'Your Saturday Briefing',
    'Your Sunday Briefing',
    'Your Monday Evening Briefing',  # NYTimes
    'Your Tuesday Evening Briefing',
    'Your Wednesday Evening Briefing',
    'Your Thursday Evening Briefing',
    'Your Friday Evening Briefing',
    'Your Saturday Evening Briefing',
    'Your Sunday Evening Briefing',
    "AP Top News",  # AP News
)

# Ref: https://github.com/dipanjanS/text-analytics-with-python/blob/master/New-Second-Edition/Ch05%20-%20Text%20Classification/contractions.py
with open('transform/config/contractions.json', 'r') as f:
    CONTRACTION_MAP = json.loads(f.read())