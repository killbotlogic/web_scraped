import random
import unittest
from main import Crawler
from unittest.mock import MagicMock
from unittest.mock import Mock

class TestShitWorks(unittest.TestCase):

    def setUp(self):
        self.crawler = Crawler()
        self.crawler._load_cookies()
        self.crawler._login()

    def test_login(self):
        c = Crawler()
        c._login()
        self.assertTrue(c._is_logged_in())

    def test_still_logged_in(self):

        c = Crawler()
        self.assertTrue(c._load_cookies())
        self.assertTrue(c._is_logged_in())

    def test_get_people_i_may_know(self):
        c = Crawler()
        c.real_init()

if __name__ == '__main__':
    unittest.main()