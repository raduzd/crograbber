#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'raduz'

import dbm
import os.path
import os
import re
import logging


def load_db(db_location):
    target_dir = os.path.dirname(os.path.expanduser(db_location))
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    return dbm.open(os.path.expanduser(db_location), "c")


def audio_was_downloaded(audio_id, db):
    return audio_id in db


def mark_audio_as_downloaded(audio_id, db):
    db[audio_id] = ""


def detect_series(article_name):
    result = ""
    searched = re.match(".*(?=\s\(\s?\d*\/\d*\s?\))", article_name)
    # searched = re.match(".*(?=\s\(\s?\d*\sz\s\d*\s?\))", article_name)
    if searched:
        result = searched.group()
    return result


def detect_episode_number(article_name):
    result = 0
    ep_number = re.search("(?<=.\s\()\d*(?=\/\d*\))", article_name)
    if ep_number:
        result = int(ep_number.group())
    return result


