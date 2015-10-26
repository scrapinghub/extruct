# -*- coding: utf-8 -*-
import json
import unittest

from extruct.w3cmicrodata import MicrodataExtractor
from tests import get_testdata

class TestMicrodata(unittest.TestCase):

    maxDiff = None

    def test_schemaorg_CreativeWork(self):
        for i in [1]:
            body = get_testdata('schema.org', 'CreativeWork.{:03d}.html'.format(i))
            expected = json.loads(get_testdata('schema.org', 'CreativeWork.{:03d}.json'.format(i)).decode('UTF-8'))

            mde = MicrodataExtractor()
            data = mde.extract(body)
            self.assertDictEqual(data, expected)

    def test_schemaorg_LocalBusiness(self):
        for i in [2, 3]:
            body = get_testdata('schema.org', 'LocalBusiness.{:03d}.html'.format(i))
            expected = json.loads(get_testdata('schema.org', 'LocalBusiness.{:03d}.json'.format(i)).decode('UTF-8'))

            mde = MicrodataExtractor()
            data = mde.extract(body)
            self.assertDictEqual(data, expected)

    def test_schemaorg_MusicRecording(self):
        for i in [1]:
            body = get_testdata('schema.org', 'MusicRecording.{:03d}.html'.format(i))
            expected = json.loads(get_testdata('schema.org', 'MusicRecording.{:03d}.json'.format(i)).decode('UTF-8'))

            mde = MicrodataExtractor()
            data = mde.extract(body)
            self.assertDictEqual(data, expected)

    def test_schemaorg_Event(self):
        for i in  [1, 2, 3, 4, 8]:
            body = get_testdata('schema.org', 'Event.{:03d}.html'.format(i))
            expected = json.loads(get_testdata('schema.org', 'Event.{:03d}.json'.format(i)).decode('UTF-8'))

            mde = MicrodataExtractor()
            data = mde.extract(body)
            self.assertDictEqual(data, expected)

    def test_w3c_5_2(self):
        body = get_testdata('w3c', 'microdata.5.2.html')
        expected = json.loads(get_testdata('w3c', 'microdata.5.2.json').decode('UTF-8'))

        mde = MicrodataExtractor(strict=True)
        data = mde.extract(body)
        self.assertDictEqual(data, expected)

    def test_w3c_5_3(self):
        body = get_testdata('w3c', 'microdata.5.3.html')
        expected = json.loads(get_testdata('w3c', 'microdata.5.3.json').decode('UTF-8'))

        mde = MicrodataExtractor(strict=True)
        data = mde.extract(body)
        self.assertDictEqual(data, expected)

    def test_w3c_5_5(self):
        body = get_testdata('w3c', 'microdata.5.5.html')
        expected = json.loads(get_testdata('w3c', 'microdata.5.5.json').decode('UTF-8'))

        mde = MicrodataExtractor(strict=True)
        data = mde.extract(body)
        self.assertDictEqual(data, expected)

    def test_w3c_7_1(self):
        body = get_testdata('w3c', 'microdata.7.1.html')
        expected = json.loads(get_testdata('w3c', 'microdata.7.1.json').decode('UTF-8'))

        mde = MicrodataExtractor(strict=True)
        data = mde.extract(body, 'http://blog.example.com/progress-report')
        self.assertDictEqual(data, expected)
