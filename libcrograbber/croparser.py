#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'raduz'

from bs4 import BeautifulSoup as bs
from urllib import request
from urllib import parse
import logging
import platform
from unidecode import unidecode



def parse_master_page(master_url):
    # Process master page (http://www.rozhlas.cz/vltava/stream/), to get all URL of category subpages
    master_soup = bs(request.urlopen(master_url).read(), "html.parser")
    suburls = [item.get("href") for item in master_soup.select("div.lista-promo")[0].find_all("a")]
    logging.debug("Number of suburl:".format(len(suburls)))
    parsed_master_url = parse.urlparse(master_url)
    base_url = "{uri.scheme}://{uri.netloc}".format(uri=parsed_master_url)
    return [parse.urljoin(base_url, item) for item in suburls]


def process_subpage(subpage_url, base_url="http://www.rozhlas.cz"):
    # Returns list of URLs for all articles on all subpages. Should return unique URLs only
    soups = [bs(request.urlopen(subpage_url).read(), "html.parser")]
    multipage = soups[0].select("div.lista_nav_middle")
    if multipage:
        soups = [bs(request.urlopen(item).read(), "html.parser") for item in subpage_urls(subpage_url, soups[0])]
    page_items_urls = []
    for page in soups:
        item_urls = [parse.urljoin(base_url, item) for item in get_page_items(page.select("div.column.column-1")[0])]
        page_items_urls.extend(item_urls)
    return set(page_items_urls)


def get_page_items(column_soup):
    return [item.a["href"] for item in column_soup.select("div.readmore")]


def subpage_urls(subpage_url, page_soup):
    # Get list of URLs for pages that are longer than one page (page x of y at the bottom)
    # navbar = page_soup.select("div.lista_nav_middle")[0]
    last_page = int(page_soup.select("div.lista_nav_middle")[0].find_all("a")[1].string)
    pages = [
        parse.urlencode({"pos": 0, "mode": (last_page - 1) * 10}),
        parse.urlencode({"pos": (last_page - 1) * 10, "mode": 10}),
    ]
    splitted = parse.urlsplit(subpage_url)
    return [
        parse.urlunsplit((splitted.scheme, splitted.netloc, splitted.path, item, splitted.fragment)) for item in pages]


def parse_audio_ids(article_soup):
    # Returns list of audio IDs for article URL
    single_play = article_soup.select("a.icon.player-archive")
    if single_play:
        result = [single_play[0]["href"].split("/")[-1]]
    else:
        result = [subplayer.select("div.uniplayer")[0]["data-id"] for subplayer in article_soup.select("div.audio")]
    return result


def parse_article_description(article_soup):
    pars = article_soup.find_all("p")
    good_pars = [par for par in pars if not par.attrs]
    description = []
    for item in good_pars:
        description.append(item.text.strip() + "\n")
    return description


def process_article(article_url):
    logging.debug("Current article URL: {}".format(article_url))
    article_data = {}
    article_soup = bs(request.urlopen(article_url).read(), "html.parser").find(id="article")
    article_data["audio_ids"] = parse_audio_ids(article_soup)
    article_data["name"] = article_soup.h1.text.strip()
    # if platform.system() == "Windows":
        #article_data["name"] = unidecode(article_data["name"])
    article_data["name"] = sanitize_article_name(article_data["name"])
    article_data["description"] = parse_article_description(article_soup)
    return article_data

def sanitize_article_name(raw_name):
    raw_name = raw_name.replace("/", " z ")
    if platform.system() == "Windows":
        raw_name = raw_name.replace(":", " -")
    return raw_name


if __name__ == "__main__":
    pass
