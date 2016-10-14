# -*- coding: utf-8 -*-
import json
from pprint import pformat
import unittest

from extruct.rdfa import RDFaExtractor
from tests import get_testdata

def tupleize(d):
    if isinstance(d, list):
        return sorted(tupleize(e) for e in d)
    if isinstance(d, dict):
        return sorted((k, tupleize(v)) for k, v in d.items())
    return d

class TestRDFa(unittest.TestCase):

    maxDiff = None

    def assertJsonLDEqual(self, a, b, normalize_bnode_ids=True):
        json_kwargs = dict(indent=2, separators=(',', ': '), sort_keys=True, ensure_ascii=True)
        sa = json.dumps(a, **json_kwargs)
        sb = json.dumps(b, **json_kwargs)
        if normalize_bnode_ids:
            sa = self.normalize_bnode_ids(sa)
            sb = self.normalize_bnode_ids(sb)
        self.assertEqual(tupleize(json.loads(sa)), tupleize(json.loads(sb)))

    def normalize_bnode_ids(self, jsld):
        import re

        bnode_ids = re.findall(r'"_:(\w+)"', jsld)
        for i, bnid in enumerate(bnode_ids, start=1):
            jsld = jsld.replace(bnid, "%06d" % i)
        return jsld

    def prettify(self, a, normalize_bnode_ids=True):
        json_kwargs = dict(indent=2, separators=(',', ': '), sort_keys=True, ensure_ascii=True)
        output = json.dumps(a, **json_kwargs)
        if normalize_bnode_ids:
            output = self.normalize_bnode_ids(output)
        return output

    def test_w3c_rdfalite(self):
        for i in [3, 4, 5]:
            fileprefix = 'w3c.rdfalite.example{:03d}'.format(i)
            body = get_testdata('w3crdfa', fileprefix + '.html').decode('UTF-8')
            expected = json.loads(
                    get_testdata('w3crdfa', fileprefix + '.expanded.json'
                ).decode('UTF-8'))

            rdfae = RDFaExtractor()
            data = rdfae.extract(body, url='http://www.example.com/index.html')
            self.assertJsonLDEqual(data, expected)

    def test_w3c_rdf11primer(self):
        for i in [14]:
            fileprefix = 'w3c.rdf11primer.example{:03d}'.format(i)
            body = get_testdata('w3crdfa', fileprefix + '.html').decode('UTF-8')
            expected = json.loads(
                    get_testdata('w3crdfa', fileprefix + '.expanded.json'
                ).decode('UTF-8'))

            rdfae = RDFaExtractor()
            data = rdfae.extract(body, url='http://www.exaple.com/index.html')
            self.assertJsonLDEqual(data, expected)

    def test_w3c_rdfaprimer(self):
        for i in [5, 6, 7, 8, 9, 10, 11, 15]:
            fileprefix = 'w3c.rdfaprimer.example{:03d}'.format(i)
            print(fileprefix)
            body = get_testdata('w3crdfa', fileprefix + '.html').decode('UTF-8')
            expected = json.loads(
                    get_testdata('w3crdfa', fileprefix + '.expanded.json'
                ).decode('UTF-8'))

            rdfae = RDFaExtractor()
            data = rdfae.extract(body, url='http://www.example.com/index.html')
            print("extracted:\n%s" % pformat(tupleize(data)))
            print("expected:\n%s" % pformat(tupleize(expected)))
            print("extracted:\n%s" % self.prettify(data))
            print("expected:\n%s" % self.prettify(expected))
            self.assertJsonLDEqual(data, expected)
