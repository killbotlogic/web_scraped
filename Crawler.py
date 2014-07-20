from bs4 import BeautifulSoup
import itertools
import random
from http import cookiejar
import os
import re
from urllib import parse
from urllib.parse import urlparse, parse_qs
from urllib import request
from urllib import error
import json
import copy
import random
import queue
from Profile import Profile


class Crawler(object):
    everybody = {}
    cookie_filename = "user_cookies.txt"
    username = 'vanessa.kennedy.mccarthy@gmail.com'
    password = 'Password29'

    root_id = 319955720
    jar = cookiejar.MozillaCookieJar(cookie_filename)
    opener = None
    _cookies_loaded = False
    root_profile = None

    @staticmethod
    def _create_opener():
        if Crawler.opener is not None:
            return

        password_manager = request.HTTPPasswordMgrWithDefaultRealm()
        password_manager.add_password(None, "https://www.linkedin.com/", Crawler.username, Crawler.password)

        Crawler.opener = request.build_opener(request.HTTPCookieProcessor(Crawler.jar),
                                              request.HTTPRedirectHandler(),
                                              request.HTTPHandler(debuglevel=0),
                                              request.HTTPSHandler(debuglevel=0),
                                              request.HTTPBasicAuthHandler(password_manager))

        Crawler.opener.addheaders = [('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')]
        Crawler.opener.addheaders = [('Accept-Encoding', 'gzip, deflate')]
        Crawler.opener.addheaders = [('Accept-Language', 'en-US,en;q=0.5')]
        Crawler.opener.addheaders = [
            ('User-Agent', 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:26.0) Gecko/20100101 Firefox/26.0')]
        request.install_opener(Crawler.opener)

    @staticmethod
    def _load_cookies():
        if Crawler._cookies_loaded:
            return True

        if os.access(Crawler.cookie_filename, os.F_OK):
            Crawler.jar.load(Crawler.cookie_filename)
            Crawler._cookies_loaded = True
            return True
        return False


    def __init__(self):
        self._create_opener()
        self._load_cookies()

        self._load_cookies()
        self._login()

        self.soup = None  # Beautiful Soup object
        self.links = set()  # Queue with every links fetched
        self.visited_links = set()
        self._people_you_may_know_ids = []
        self._people_you_may_know_urls = []
        self.people_you_may_know = []
        self._people_ids = []
        self._people_urls = []
        self.people_also_viewed = []

        self.counter = 0  # Simple counter for debug purpose

        self.root_profile = Profile('http://www.linkedin.com/profile/view?id={}'.format(Crawler.root_id))
        self.root_profile._load_html()

        self.connected_profile_ids = self.root_profile.connected_profile_ids


    def _is_logged_in(self):
        res = request.urlopen("https://www.linkedin.com/profile/view?id=319955720")
        if res.geturl() == "https://www.linkedin.com/profile/view?id=319955720":
            return True
        return False

    def _login(self):
        """
        Handle login. This should populate our cookie jar.
        """
        if self._is_logged_in():
            return

        html = request.urlopen("https://www.linkedin.com/uas/login").read()
        soup = BeautifulSoup(html)
        csrf = soup.find(id="loginCsrfParam-login")['value']

        login_data = parse.urlencode({
            'session_key': self.username,
            'session_password': self.password,
            'loginCsrfParam': csrf
        })

        data = login_data.encode()

        response = request.urlopen("https://www.linkedin.com/uas/login-submit", data)

        self.jar.save(self.cookie_filename)

        return response

    def harvest(self, num=-1):

        pass

    def run(self, num):

        scraping = set()
        p = self.root_profile
        p._load_html()

        for i in range(0, num):

            print('starting {}'.format(p.url))
            print('\t {}'.format(p.name))
            for random_dude in p.people_also_viewed:
                if random_dude.profile_id in Profile.population_database:
                    continue
                if random_dude in scraping:
                    continue
                scraping.add(random_dude)

            p = scraping.pop()
            p._load_html()