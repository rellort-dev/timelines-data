
import pytest
import random

from embed import is_problematic_article
import embed.config as embed_config


problematic_phrase = random.choice(embed_config.ARTICLES_TO_REMOVE)
@pytest.mark.parametrize(
    "article, expected_result", 
    [
        ({}, True),
        ({"description": ""}, True),
        ({"title": problematic_phrase}, True),
        ({"title": f"{problematic_phrase} end"}, True),
        ({"title": f"start {problematic_phrase}"}, False),
        ({"title": f"start {problematic_phrase} end"}, False),
        ({"title": ""}, False),
        ({"title": "", "description": problematic_phrase}, False),
    ]
)
def test_is_problematic_article(article, expected_result):
    assert is_problematic_article(article) == expected_result
