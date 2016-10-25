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
    argparser.add_argument("--db", help="Download history location", default="~/.crograbber/history.db")
    argparser.add_argument("--use-subdirs", "-c", help="Creater a subdirectory for every downloaded article")
    return argparser.parse_args()


def process_master_page(url):
    sub_pages = croparser.parse_master_page(url)
    return [process_sub_page(sub_page) for sub_page in sub_pages]


def process_sub_page(url):
    articles = croparser.process_subpage(url)
    return [process_article(article) for article in articles]


def process_article(url):
    return croparser.process_article(url)


def do_full_auto(url, argparser):
    db = automat.load_db(argparser.db)
    real_path = os.path.expanduser(argparser.directory)
    articles = process_master_page(url)
    if not os.path.exists(real_path) and argparser.download:
        raise FileNotFoundError("Target directory doesn't exist.")
    for article in articles:
        article["audio_ids"] = filterfalse(lambda audio_id: audio_id in db, article["audio_ids"])
        series = automat.detect_series(article["name"])
        if series:
            url_downloader.download_audio_for_article(article, os.path.join(real_path, series), True)

def main():
    argparser = create_arg_parser()
    if argparser.masterpage:
        articles = process_master_page(argparser.url)
    elif argparser.subpage:
        articles = process_sub_page(argparser.url)
    else:
        articles = [process_article(argparser.url)]
        real_path = os.path.expanduser(argparser.directory)
        if not os.path.exists(real_path) and argparser.download:
            raise FileNotFoundError("Target directory doesn't exist.")

    for article in articles:
        if argparser.download:
            url_downloader.download_audio_for_article(article, real_path)
        else:
            for audio_id in article["audio_ids"]:
                print(url_downloader.generate_audio_url(audio_id))


if __name__ == "__main__":
    main()
