#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'raduz'

import pycurl
import os.path
import sys
from progressbar import ProgressBar, FileTransferSpeed, Bar, Percentage, Counter,DataSize, AdaptiveETA, AdaptiveTransferSpeed, SimpleProgress, DataTransferBar
from crograbber import automat
import logging

AUDIO_URL_TEPMLATE = "http://media.rozhlas.cz/_audio/{}.mp3"
SINGLE_PLAY_TEMPLATE = "{name}.mp3"
MULTI_PLAY_TEMPLATE = "{name} - {number}.mp3"
DESCRIPTION_FILENAME_TEMPLATE = "{}.txt"


def generate_audio_url(audio_id):
    return AUDIO_URL_TEPMLATE.format(audio_id)


def download_audio_for_article(article, base_path, fullauto=False):
    os.makedirs(base_path, exist_ok=True)
    if fullauto:
        starter = int(automat.detect_episode_number(article["name"]))
    else:
        starter = 0 if len(article["audio_ids"]) == 1 else 1
    base_file_name = os.path.join(base_path,generate_file_name_base(article))
    output_file_name_desc = DESCRIPTION_FILENAME_TEMPLATE.format(base_file_name)

    write_description(article, output_file_name_desc)
    for item in enumerate(article["audio_ids"], starter):
        output_file_name = generate_audio_file_name(base_file_name, item[0],original_length=len(article["audio_ids"]) )
        logging.debug("Current article name: {}".format(article["name"]))
        logging.debug("Target filename: {}".format(output_file_name))
        run_download(generate_audio_url(item[1]), output_file_name, fullauto)


def run_download(audio_url, filename, fullauto=False):
    print("Downloading {} to {}".format(audio_url, filename))
    pbar = ProgressBar(widgets=['(',SimpleProgress(),')',
                                                              Bar(), ' ',
                                                              AdaptiveTransferSpeed(), ' ',
                                                              AdaptiveETA() ]).start()
    with open(filename, "wb") as target:
        def progress_local(download_total, downloaded, upload_total, uploaded):
            pbar.max_value=download_total
            pbar.update(downloaded)
        c = pycurl.Curl()
        c.setopt(pycurl.FOLLOWLOCATION, True)
        c.setopt(pycurl.URL, audio_url)
        c.setopt(pycurl.WRITEDATA, target)
        c.setopt(pycurl.NOPROGRESS, False)
        c.setopt(pycurl.XFERINFOFUNCTION, progress_local)
        c.perform()
        pbar.finish()
        c.close()


def write_description(article, filename):
    with open(filename, "w") as target:
        target.writelines(article["description"])


def generate_file_name_base(article):

    raw_name = article["name"]
    raw_name = raw_name.replace("/"," z ")
    return raw_name


def generate_audio_file_name(file_name_base, number, original_length=1):
    name = ""
    if number > 0 and original_length > 1:
        name = MULTI_PLAY_TEMPLATE.format(name=file_name_base,number=number)
    else:
        name = SINGLE_PLAY_TEMPLATE.format(name=file_name_base)
    return name
