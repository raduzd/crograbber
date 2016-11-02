#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'raduz'

from libcrograbber import croparser
from libcrograbber import url_downloader
from libcrograbber import automat
import argparse
import os.path
import sys
from itertools import filterfalse
import logging
import platform
if platform.system() == "Windows":
    import win-unicode-console
    win-unicode-console.enable()

DEFAULT_CFG_DIR = "~/.crograbber"


def create_arg_parser():
    argparser = argparse.ArgumentParser(description="Audio grabber for Cesky Rozhlas (Czech Radio)")
    group_type = argparser.add_mutually_exclusive_group()
    argparser.add_argument("url", help="URL of the page to process")
    group_type.add_argument("-a", "--article", action="store_true", default=True,
                            help="Consider url to be a single article (default)")
    group_type.add_argument("-s", "--subpage", action="store_true",
                            help="Consider url to be a subpage containing multiples articles")
    group_type.add_argument("-m", "--masterpage", action="store_true",
                            help="Consider url to be a masterpage containing multiple subpages")
    argparser.add_argument("--download", action="store_true",
                           help="Download resulting audio URLs. Normally audio URL are only displayed")
    argparser.add_argument("--directory", "-d", help="Directory for saving downloaded files", default="./")
    argparser.add_argument("--fullauto", help="Fully automatic mode - use with caution", action="store_true")
    argparser.add_argument("--db", help="Download history location", default=os.path.join(DEFAULT_CFG_DIR, "history"))
    argparser.add_argument("--debug", help="Enable debuging messages", action="store_true")
    return argparser.parse_args()


def process_master_page(url):
    logging.debug("Processing master page {}".format(url))
    sub_pages = croparser.parse_master_page(url)
    articles = []
    for item in sub_pages:
        articles.extend(process_sub_page(item))
    # return [process_sub_page(sub_page) for sub_page in sub_pages]
    return articles


def process_sub_page(url):
    logging.debug("Processing subpage {}".format(url))
    articles = croparser.process_subpage(url)
    return [process_article(article) for article in articles]


def process_article(url):
    logging.debug("Processing article {}".format(url))
    return croparser.process_article(url)


def do_full_auto(articles, argparser, real_path):
    with automat.load_db(os.path.expanduser(argparser.db)) as db:
        for article in articles:
            logging.debug("Article name: {}, article audio_ids: {}".format(article["name"], article["audio_ids"]))
            article["audio_ids"] = list(
                filterfalse(lambda audio_id: db.get(audio_id, "") == b"1", article["audio_ids"]))
            series = automat.detect_series(article["name"])
            if series:
                starter = int(automat.detect_episode_number(article["name"]))
                series_path = os.path.join(real_path, series)
                os.makedirs(series_path, exist_ok=True)
                if len(article["audio_ids"]):
                    url_downloader.write_description(article, series_path, series)
                url_downloader.download_audio_for_article(article, series_path, starter, fullauto=True)
            else:
                starter = 1 if len(article["audio_ids"]) > 1 else 0
                desc_path = os.path.join(real_path, article["name"])
                os.makedirs(real_path, exist_ok=True)
                if len(article["audio_ids"]):
                    url_downloader.write_description(article, desc_path, series)
                url_downloader.download_audio_for_article(article, real_path, starter, fullauto=True)

            for item in article["audio_ids"]:
                db[item] = "1"


def do_manual_mode(articles, argparser, real_path):
    for article in articles:
        starter = 0 if len(article["audio_ids"]) == 1 else 1
        if argparser.download:
            desc_path = os.path.join(real_path, article["name"])
            url_downloader.write_description(article, desc_path)
            url_downloader.download_audio_for_article(article, real_path, starter)
        else:
            for audio_id in article["audio_ids"]:
                print(url_downloader.generate_audio_url(audio_id))


def main():
    argparser = create_arg_parser()
    if argparser.debug:
        logging.basicConfig(filename='crograbber.log', level=logging.DEBUG)
    if not os.path.exists(os.path.expanduser(DEFAULT_CFG_DIR)):
        os.makedirs(DEFAULT_CFG_DIR)
    if argparser.masterpage:
        articles = process_master_page(argparser.url)
    elif argparser.subpage:
        articles = process_sub_page(argparser.url)
    else:
        articles = [process_article(argparser.url)]
    real_path = os.path.expanduser(argparser.directory)
    if not os.path.exists(real_path) and argparser.download:
        raise FileNotFoundError("Target directory doesn't exist.")

    if argparser.fullauto:
        do_full_auto(articles, argparser, real_path)
    else:
        do_manual_mode(articles, argparser, real_path)


if __name__ == "__main__":
    main()
