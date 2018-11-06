import unittest
from tropopause.validators import valid_url


class TestValidators(unittest.TestCase):
    """ Unit Tests for tropopause.validators """

    def test_valid_urls(self):
        urls = [
            "http://www.example.com",
            "https://www.example.com",
            "http://www.example.com/",
            "http://www.example.com/test",
            "http://www.example.com/test/",
            "http://www.example.com/test/test",
            "http://www.example.com/test.html",
        ]
        for url in urls:
            self.assertEqual(url, valid_url(url))

    def test_invalid_path(self):
        url = "http://www.example.com/test!.html"
        with self.assertRaises(ValueError):
            valid_url(url)

    def test_invalid_domain(self):
        url = "http://www.example!.com/"
        with self.assertRaises(ValueError):
            valid_url(url)

    def test_invalid_protocol(self):
        url = "ftp://www.example.com/test.html"
        with self.assertRaises(ValueError):
            valid_url(url)
