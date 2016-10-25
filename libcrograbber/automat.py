#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'raduz'

from libcrograbber import url_downloader
import dbm
import os.path
import os


def load_db(db_location):
    target_dir = os.path.dirname(os.path.expanduser(db_location))
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    return dbm.open(db_location, "c")


def audio_was_downloaded(audio_id, db):
    return audio_id in db


def mark_audio_as_downloaded(audio_id, db):
    db[audio_id] = ""