import random
import unittest
from main import Crawler, Profile
from unittest.mock import MagicMock
from unittest.mock import Mock
import json
from urllib.parse import urlparse, parse_qs


class MockCrawler(Crawler):
    def __init__(self):
        self._create_opener()
        self._load_cookies()

class MockProfile(Profile):
    pass


class TestShitWorks(unittest.TestCase):

    def setUp(self):


        self.profile = None

    @classmethod
    def setUpClass(cls):
        print('Creating Crawler')
        cls.crawler = Crawler()


    def test_login(self):
        c = MockCrawler()
        MockCrawler.jar.clear()
        MockCrawler._cookies_loaded = False
        self.assertFalse(c._is_logged_in())
        c._login()
        self.assertTrue(c._is_logged_in())

    # "wtf"
    def test_still_logged_in(self):
        c = MockCrawler()
        self.assertTrue(c._load_cookies())
        self.assertTrue(c._is_logged_in())

    def test_init_profile_from_url(self):

        p = Profile(url='/profile/view?id=319955720')
        self.assertEquals(p.url, 'https://www.linkedin.com/profile/view?id=319955720')
        self.assertEquals(p.profile_id, 319955720)




    def test_people_also_viewed(self):
        link = self.crawler.root_profile.people_also_viewed[0].url

        p = Profile(link)
        p._load_html()
        assert len(p.people_also_viewed) >= 1


    def test_parse_premium_user(self):
        p = Profile(url='/profile/view?id=1040844&authType=name&authToken=_P15')
        p._load_html()

    def test_harvesting(self):
        self.crawler.run(1000)
        #p = self.crawler.people_you_may_know[0].people_also_viewed[0].people_also_viewed[0].people_also_viewed[0]

    def test_dump_stuff(self):
        p = self.crawler.root_profile.people_also_viewed[0]
        p._load_html()
        Profile.dump_stuff('{}.json'.format(p.profile_id), json.dumps(p.top_card))

    def test_profile_with_no_people_also_viewed(self):
        p = MockProfile(url='http://www.linkedin.com/profile/view?id=30936168&authType=name&authToken=OusF')
        p._load_html()
        self.assertListEqual(p.people_also_viewed, [])

    def test_people_with_no_first_and_last_name(self):
        p = MockProfile(url='https://www.linkedin.com/profile/view?id=304000038&authType=name&authToken=nI2a')
        p._load_html()
        assert p.first_name is None
        assert p.last_name is None


    def test_people_lists_not_same(self):
        p1 = self.crawler.root_profile
        p2 = self.crawler.root_profile.people_also_viewed[1]
        p1_clone = MockProfile(p1.url)

        assert len(p1.people_also_viewed) >= 1
        assert p2.people_also_viewed == []
        assert p1_clone.people_also_viewed == []

        p2._load_html()
        p1_clone._load_html()
        assert set(p1.people_also_viewed) != set(p2.people_also_viewed)
        self.assertListEqual(p1.people_also_viewed, p1_clone.people_also_viewed)


if __name__ == '__main__':
    unittest.main()