import random
import unittest
from main import Crawler, Profile
from unittest.mock import MagicMock
from unittest.mock import Mock

class TestShitWorks(unittest.TestCase):

    def setUp(self):


        self.profile = None

    @classmethod
    def setUpClass(cls):
        cls.crawler = Crawler()
        cls.crawler.real_init()
        pass

    def test_login(self):
        c = Crawler()
        Crawler.jar.clear()
        Crawler._cookies_loaded = False
        self.assertFalse(c._is_logged_in())
        c._login()
        self.assertTrue(c._is_logged_in())

    def test_still_logged_in(self):

        c = Crawler()
        self.assertTrue(c._load_cookies())
        self.assertTrue(c._is_logged_in())

    def test_get_people_i_may_know(self):
        c = Crawler()
        c.real_init()
        self.assertEquals(len(c._people_you_may_know_ids), 4)
        assert len(c._people_you_may_know_urls) == 4
        self.assertEquals(len(c.people_you_may_know), 4)
        assert len(Profile.population_database) == 4

    def test_init_profile_from_url(self):

        p = Profile(url='/profile/view?id=319955720')
        self.assertEquals(p.url, 'https://www.linkedin.com/profile/view?id=319955720')
        self.assertEquals(p.profile_id, 319955720)

    def test_people_also_viewed(self):
        p = Profile(self.crawler._people_you_may_know_urls[0])
        p._load_people_also_viewed()
        assert len(p.people_also_viewed) == 10

if __name__ == '__main__':
    unittest.main()