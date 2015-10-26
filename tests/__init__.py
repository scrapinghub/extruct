# -*- coding: utf-8 -*-
import os

tests_datadir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'samples')

def get_testdata(*paths):
    """Return test data"""
    path = os.path.join(tests_datadir, *paths)
    return open(path, 'rb').read()
