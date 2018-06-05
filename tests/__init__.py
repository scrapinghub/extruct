# -*- coding: utf-8 -*-
import os
import json


tests_datadir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'samples')


def get_testdata(*paths):
    """Return test data"""
    path = os.path.join(tests_datadir, *paths)
    with open(path, 'rb') as f_in:
        return f_in.read()


def jsonize_dict(d):
    return json.loads(json.dumps(d))
