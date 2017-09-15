import unittest
from tropopause import Tags
from troposphere import Tags as upstreamTags


class TestTags(unittest.TestCase):
    def test_tag_is_correct_class(self):
        tag = Tags()
        self.assertIsInstance(
            tag,
            upstreamTags
        )

    def test_tag_simple_concatanation(self):
        t1 = Tags(a='a')
        t2 = Tags(b='b')
        test_tags = t1 + t2
        self.assertEqual(2, len(test_tags.tags))

    def test_tag_complex_concatanation(self):
        t1 = Tags(a='foo')
        t2 = Tags(a='bar', b='baz')
        test_tags = t1 + t2
        self.assertEqual(2, len(test_tags.tags))
        self.assertIn({'Key': 'a', 'Value': 'bar'}, test_tags.tags)
        self.assertIn({'Key': 'b', 'Value': 'baz'}, test_tags.tags)
