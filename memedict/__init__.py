#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Knowyourmeme.com definitions scraper.
"""

import requests
from bs4 import BeautifulSoup
from difflib import SequenceMatcher


SEARCH_SIMILARITY_THRESHOLD = .4

HEADERS = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36')}


def search_meme(text):
    """Return a meme name and url from a meme keywords.
    """
    r = requests.get('http://knowyourmeme.com/search?q=%s' % text, headers=HEADERS)
    soup = BeautifulSoup(r.text, 'html.parser')
    memes_list = soup.find(class_='entry_list')
    if memes_list:
        # Get all unique returned meme paths
        meme_paths = [meme['href'] for meme in memes_list.find_all('a', class_='photo', href=True)]
        meme_paths = list(set(meme_paths))
        # Get the meme template names and URLs from the meme paths
        meme_names = [meme_path.split('/')[-1].replace('-', ' ') for meme_path in meme_paths]
        meme_urls = ['https://knowyourmeme.com%s' % meme_path for meme_path in meme_paths]
        return list(zip(meme_names, meme_urls))
    return None


def search(text):
    """Return a meme definition from a meme keywords.
    """
    memes = search_meme(text)
    if memes is None:
        return None

    # Get sequence match scores between each meme template name search text
    meme_scores = [SequenceMatcher(None, text, meme[0]).ratio() for meme in memes]

    # Get the best matching meme and its name and URL
    best_meme_score = max(meme_scores)
    best_meme = memes[meme_scores.index(best_meme_score)]
    meme_name, url = best_meme[0], best_meme[1]

    if meme_name and best_meme_score >= SEARCH_SIMILARITY_THRESHOLD:
        r = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(r.text, 'html.parser')
        entry = soup.find('h2', {'id': 'about'})
        return entry.next.next.next.text

    return None
