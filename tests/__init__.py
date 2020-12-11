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


def replace_node_ref_with_node_id(item):
    if isinstance(item, list):
        for i in item:
            replace_node_ref_with_node_id(i)
    if isinstance(item, dict):
        for key in list(item):
            val = item[key]
            if key == "htmlNode":
                item["_nodeId_"] = val.getAttribute("id")
                del item[key]
            else:
                replace_node_ref_with_node_id(val)
