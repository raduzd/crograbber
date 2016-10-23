#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'raduz'

from libcrograbber import croparser
from libcrograbber import url_downloader
import argparse


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
    return argparser.parse_args()


def process_master_page(url):
    sub_pages = croparser.parse_master_page(url)
    return [process_sub_page(sub_page) for sub_page in sub_pages]


def process_sub_page(url):
    articles = croparser.process_subpage(url)
    return [process_article(article) for article in articles]


def process_article(url):
    return croparser.process_article(url)

def main():
    argparser = create_arg_parser()
    if argparser.masterpage:
        articles = process_master_page(argparser.url)
    elif argparser.subpage:
        articles = process_sub_page(argparser.url)
    else:
        articles = [process_article(argparser.url)]
    if argparser.download:
        for article in articles:
            url_downloader.download_audio_for_article(article)


if __name__ == "__main__":
    main()
