import random
import unittest
from urllib import request
from bs4 import BeautifulSoup
from Crawler import Crawler
from Profile import Profile
from unittest.mock import MagicMock
from unittest.mock import Mock
import json
from urllib.parse import urlparse, parse_qs


class MockCrawler(Crawler):
    def __init__(self):
        self._create_opener()
        self._load_cookies()

class MockProfile(Profile):
    def __init__(self):
        pass


class TestShitWorks(unittest.TestCase):

    def setUp(self):
        # self.profile = None
        pass

    @classmethod
    def setUpClass(cls):
        # print('Creating Crawler')
        # cls.crawler = Crawler()
        pass


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

    # cant test this because it aint gonna happen
    # def test_profile_with_no_connected_profile_ids(self):
    # p = MockProfile(url='http://www.linkedin.com/profile/view?id=30936168&authType=name&authToken=OusF')
    #     p._load_html()
    #     self.assertListEqual(p.connected_profile_ids, [])

    def test_people_with_no_first_and_last_name(self):
        p = MockProfile(url='https://www.linkedin.com/profile/view?id=304000038&authType=name&authToken=nI2a')
        p._load_html()
        assert p.first_name is None
        assert p.last_name is None


    def test_extract_related_profile_ids_from_html(self):
        res = request.urlopen(
            'https://www.linkedin.com/profile/view?id=1535870&authType=name&authToken=tDG2&offset=5&trk=prof-sb-pdm-similar-photo')
        self.html = res.read()

        soup = BeautifulSoup(self.html)
        ids = Profile.get_related_profile_ids(soup)

        assert 732590 in ids
        assert 90584941 in ids
        assert 20390197 in ids

    # make sure ya got an auth token in the url
    
    def test_extract_full_name_from_html(self):
        res = request.urlopen(
            'https://www.linkedin.com/profile/view?id=1535870&authType=name&authToken=tDG2&offset=5&trk=prof-sb-pdm-similar-photo')
        self.html = res.read()

        soup = BeautifulSoup(self.html)
        self.assertEqual(Profile.get_full_name(soup), 'Patrick Armitage')


    def test_extract_last_name_from_html(self):
        """
        &lastName=???

        https://www.linkedin.com/profile/view?id=28862512&authType=name&authToken=Aggs&offset=1&trk=prof-sb-pdm-similar-name == Smith

        """



        # Profile._get_last_name(soup)
        pass

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


    def test_view_private_profile(self):
        """
        https://www.linkedin.com/profile/view?id=153703062&authToken=FfR6&trk=prof-exp-snippet-endorsement-name
        """
        pass

    def test_extract_user_id_from_url(self):
        """

        connect
        /people/invite?from=profile&key=39728594&firstName=Meng&lastName=Her&authToken=FJzc&authType=name&csrfToken=ajax%3A2844583125699424377&goback=%2Enpv_77380503_*1_*1_OUT*4OF*4NETWORK_NdaA_*1_en*4US_*1_*1_*1_3199557201405855731157_3_8_*1_*1_*1_*1_*1_*1_*1_*1_*1_*1_*1_*1_*1_*1_*1_*1_*1_*1_*1_*1_*1_*1_vsrp*4people*4res*4name*4headless_*1&trk=prof-sb-pdm-search-connect


        """
        p = MockProfile()

        assert p.get_user_id(
            'https://www.linkedin.com/profile/view?id=106043148&authType=name&authToken=oJ51&offset=3&trk=prof-sb-pdm-similar-name') == 106043148
        assert p.get_user_id(
            'https://www.linkedin.com/profile/view?id=34207573&authType=name&authToken=lTP0&offset=2&trk=prof-sb-pdm-similar-photo') == 34207573
        assert p.get_user_id(
            'https://www.linkedin.com/profile/view?id=106043148&authType=name&authToken=oJ51&offset=3&trk=prof-sb-pdm-similar-photo') == 106043148
        assert p.get_user_id(
            'https://www.linkedin.com/profile/view?id=31189957&authType=name&authToken=TixA&offset=4&trk=prof-sb-pdm-similar-photo') == 31189957
        assert p.get_user_id(
            'https://www.linkedin.com/profile/view?id=74926529&authType=name&authToken=C5wx&offset=5&trk=prof-sb-pdm-similar-photo') == 74926529
        assert p.get_user_id(
            'https://www.linkedin.com/profile/view?id=8306764&authType=name&authToken=lp-f&offset=3&trk=prof-sb-pdm-similar-name') == 8306764


if __name__ == '__main__':
    unittest.main()