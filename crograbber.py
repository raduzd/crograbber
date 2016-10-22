#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'raduz'

from libcrograbber import croparser
import argparse

def create_arg_parser():
    argparser = argparse.ArgumentParser(description="Audio grabber for Cesky Rozhlas (Czech Radio)")
    group_type = argparser.add_mutually_exclusive_group()
    argparser.add_argument("url", help="URL of the page to process")
    group_type.add_argument("-a", "--article", action="store_true", default=True,
                            help = "Consider url to be a single article (default)")
    group_type.add_argument("-s", "--subpage", action="store_true",
                            help = "Consider url to be a subpage containing multiples articles")
    group_type.add_argument("-m", "--masterpage", action="store_true",
                            help = "Consider url to be a masterpage containing multiple subpages")
    argparser.add_argument("--download", action="store_true",
                           help = "Download resulting audio URLs. Normally audio URL are only displayed")
    return argparser.parse_args()


def main():
    argparser = create_arg_parser()


if __name__ == "__main__":
    main()
