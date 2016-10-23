#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'raduz'

import pycurl

AUDIO_URL_TEPMLATE = "http://media.rozhlas.cz/_audio/{}.mp3"


def generate_audio_url(audio_id):
    return AUDIO_URL_TEPMLATE.format(audio_id)

