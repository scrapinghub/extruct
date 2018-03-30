# -*- coding: utf-8 -*-
import unittest
import json

from extruct import utils


class NotAJSONDecodeError(ValueError):
    pass


class _json_shimmer:
    def __init__(self):
        self.invoked = False

    def decode(self, json_string):
        if json_string == 'FAIL WITH VALUEERROR':
            raise ValueError("Yes sir")
        try:
            return json.loads(json_string)
        except utils.native_json_exc:
            raise NotAJSONDecodeError("This operation totally failed")
        finally:
            self.invoked = True


class TestJson(unittest.TestCase):

    def test_json_abstraction(self):
        # Use default decoder
        self.assertEqual(utils._json_decoder, json.loads)
        self.assertEqual(utils._json_decoder_raises, tuple())
        self.assertEqual(utils.json_loads('{}'), {})
        with self.assertRaises(utils.native_json_exc):  # ugh, Python 2
            utils.json_loads('{')
        # Set decoder, try again
        shimmer = _json_shimmer()
        utils.set_json_decoder(shimmer.decode, (NotAJSONDecodeError,))
        self.assertEqual(utils._json_decoder, shimmer.decode)
        self.assertEqual(utils._json_decoder_raises, (NotAJSONDecodeError,))
        self.assertEqual(utils.json_loads('{}'), {})
        # ensure utils.json_loads didn't call a stale reference to json.loads
        self.assertTrue(shimmer.invoked)
        # Specified exceptions should be converted to JSONDecodeErrors.
        with self.assertRaises(utils.native_json_exc):
            utils.json_loads('{')
        # Others should not.
        with self.assertRaises(ValueError):
            utils.json_loads('FAIL WITH VALUEERROR')
