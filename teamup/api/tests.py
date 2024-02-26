from django.test import TestCase

# Create your tests here.
class CacheTest(TestCase):
    def test_cache_set(self):
        self.assertIsNotNone(1)