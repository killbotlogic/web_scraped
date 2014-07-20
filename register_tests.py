import random
import unittest
import uuid
from main import Crawler, Profile
from unittest.mock import MagicMock
from unittest.mock import Mock
import json
from urllib.parse import urlparse, parse_qs
import registration
from registration import Registration


class MockCrawler(Crawler):
    def __init__(self):
        self._create_opener()
        self._load_cookies()


class MockProfile(Profile):
    pass


class TestRegister(unittest.TestCase):
    def setUp(self):
        self.profile = None

    @classmethod
    def setUpClass(cls):
        print('Creating Crawler')
        cls.crawler = MockCrawler()

    def test_register(self):
        register = Registration()
        profile = register.create_profile('vanessa.kennedy.mccarthy@gmail.com', 'Password29', profile_id=319955720)
        self.assertTrue(isinstance(profile, Profile))

    def test_new_registration_logging_in(self):
        profile = Registration().create_profile('vanessa.kennedy.mccarthy@gmail.com', 'Password29',
                                                profile_id=319955720)
        profile.log_in()
        self.assertTrue(profile.is_logged_in())

    def test_new_registration_with_custom_details(self):
        profile = Registration().create_profile()
        profile.log_in()
        self.assertTrue(profile.is_logged_in())
        pass


if __name__ == '__main__':
    unittest.main()