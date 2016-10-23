#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'raduz'

import pycurl

AUDIO_URL_TEPMLATE = "http://media.rozhlas.cz/_audio/{}.mp3"
SINGLE_PLAY_TEMPLATE = "{name}.mp3"
MULTI_PLAY_TEMPLATE = "{name} - {number}.mp3"
DESCRIPTION_FILENAME_TEMPLATE = "{}.txt"


def generate_audio_url(audio_id):
    return AUDIO_URL_TEPMLATE.format(audio_id)


def download_audio_for_article(article):
    starter = 0 if len(article["audio_ids"]) == 1 else 1
    base_file_name = generate_file_name_base(article)
    output_file_name_desc = DESCRIPTION_FILENAME_TEMPLATE.format(base_file_name)
    write_description(article, output_file_name_desc)
    for item in enumerate(article["audio_ids"], starter):
        output_file_name = generate_audio_file_name(base_file_name, item[0])
        run_download(generate_audio_url(item[1]), output_file_name)


def run_download(audio_url, filename):
    with open(filename, "wb") as target:
        print("Downloading {} to {}".format(audio_url, filename))
        c = pycurl.Curl()
        c.setopt(pycurl.FOLLOWLOCATION, True)
        c.setopt(pycurl.URL, audio_url)
        c.setopt(pycurl.WRITEDATA, target)
        c.perform()
        c.close()


def write_description(article, filename):
    with open(filename, "w") as target:
        print("Writing description to {}".format(filename))
        target.write(article["description"])


def generate_file_name_base(article):
    raw_name = article["name"]
    raw_name = raw_name.replace("/"," z ")
    return raw_name


def generate_audio_file_name(file_name_base, number):
    name = ""
    if number == 0:
        name = SINGLE_PLAY_TEMPLATE.format(name=file_name_base)
    else:
        name = MULTI_PLAY_TEMPLATE.format(name=file_name_base,number=number)
    return name
