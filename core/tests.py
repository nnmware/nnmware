# nnmware(c)2012-2017

import unittest
from .models import Tag


class TagTestCase(unittest.TestCase):
    def setUp(self):
        self.tag1 = Tag.objects.create(name="linux")
        self.tag2 = Tag.objects.create(name="cisco")
        self.tag3 = Tag.objects.create(name="python")
        self.tag4 = Tag.objects.create(name="php")

    def test_tag_count(self):
        """ Count of tags with first letter"""
        self.assertEqual(self.tag3.lettercount(), 2)
        self.assertEqual(self.tag2.lettercount(), 1)
