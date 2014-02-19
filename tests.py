import random
import unittest
from main import Crawler, Profile
from unittest.mock import MagicMock
from unittest.mock import Mock
import json


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
        cls.crawler = Crawler()
        pass

    def test_login(self):
        c = MockCrawler()
        MockCrawler.jar.clear()
        MockCrawler._cookies_loaded = False
        self.assertFalse(c._is_logged_in())
        c._login()
        self.assertTrue(c._is_logged_in())
#"wtf"
    def test_still_logged_in(self):
        c = MockCrawler()
        self.assertTrue(c._load_cookies())
        self.assertTrue(c._is_logged_in())

    def test_get_people_i_may_know(self):
        c = Crawler()
        self.assertEquals(len(c._people_you_may_know_ids), 4)
        assert len(c._people_you_may_know_urls) == 4
        self.assertEquals(len(c.people_you_may_know), 4)
        assert len(Profile.population_database) == 4

    def test_init_profile_from_url(self):

        p = Profile(url='/profile/view?id=319955720')
        self.assertEquals(p.url, 'https://www.linkedin.com/profile/view?id=319955720')
        self.assertEquals(p.profile_id, 319955720)

    def test_crawler_people_known_urls(self):
        link = self.crawler._people_you_may_know_urls[0]
        assert 'http' in self.crawler.people_you_may_know[0].url

        assert 'http' in link


    def test_people_also_viewed(self):
        link = self.crawler._people_you_may_know_urls[0]

        p = Profile(link)
        p._load_html()
        assert len(p.people_also_viewed) == 10


    def test_harvesting(self):
        self.crawler.run(1000)
        #p = self.crawler.people_you_may_know[0].people_also_viewed[0].people_also_viewed[0].people_also_viewed[0]

    def test_dump_stuff(self):
        p = self.crawler.people_you_may_know[0]
        p._load_html()
        Profile.dump_stuff('{}.json'.format(p.profile_id), json.dumps(p.top_card))

    def test_profile_with_no_people_also_viewed(self):
        p = Profile(url='http://www.linkedin.com/profile/view?id=30936168&authType=name&authToken=OusF')
        p._load_html()
        self.assertListEqual(p.people_also_viewed, [])

    def test_people_with_no_first_and_last_name(self):
        pass


if __name__ == '__main__':
    unittest.main()