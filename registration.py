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
from main import Profile
from faker import Faker


class Registration(object):
    cookie_filename = "registration_cookies.txt"

    opener = None

    jar = cookiejar.MozillaCookieJar(cookie_filename)


    @staticmethod
    def _create_opener():
        if Registration.opener is not None:
            return Registration.opener

        # password_manager = request.HTTPPasswordMgrWithDefaultRealm()
        # password_manager.add_password(None, "https://www.linkedin.com/", Registration.username, Registration.password)

        opener = request.build_opener(request.HTTPCookieProcessor(Registration.jar),
                                      request.HTTPRedirectHandler(),
                                      request.HTTPHandler(debuglevel=0),
                                      request.HTTPSHandler(debuglevel=0))

        # opener.add_handler(request.HTTPBasicAuthHandler(password_manager))

        opener.addheaders = [('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')]
        opener.addheaders = [('Accept-Encoding', 'gzip, deflate')]
        opener.addheaders = [('Accept-Language', 'en-US,en;q=0.5')]
        opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:26.0) Gecko/20100101 Firefox/26.0')]
        request.install_opener(opener)
        return opener


    def __init__(self):
        Registration.opener = self._create_opener()

    def create_profile(self, username='', password='', profile_id=0, first_name='', last_name=''):
        profile = RegisteredProfile(username, password, profile_id, first_name, last_name)
        profile.register()

        return profile


class RegisteredProfile(Profile):
    def __init__(self, username='', password='', profile_id=0, first_name='', last_name=''):

        self.faker = Faker()

        self.profile_id = profile_id
        self.thumb_src = ''
        self.image_src = ''

        self.people_also_viewed = []
        self.has_people_also_viewed = None
        self.html = None

        if first_name != '':
            self.first_name = first_name
        else:
            self.first_name = self.faker.first_name()

        if last_name != '':
            self.last_name = last_name
        else:
            self.last_name = self.faker.last_name()

        self.name = self.first_name + ' ' + self.last_name

        if username != '':
            self.username = username
        else:
            self.username = self.faker.free_email()

        if password != '':
            self.password = password
        else:
            self.password = 'S0mEfr!ck1n6P@sSw0rd'

        if self.profile_id == 0:
            self.profile_id = 0


    def register(self):
        req_html = request.urlopen("https://www.linkedin.com/reg/join").read()

        soup = BeautifulSoup(req_html)
        csrf = soup.find(id="csrfToken-coldRegistrationForm")['value']

        register_data = parse.urlencode({
            'isJsEnabled': 'true',
            'firstName': self.first_name,
            'lastName': self.last_name,
            'email': self.username,
            'password': self.password,
            'csrfToken': csrf,
            'sourceAlias': soup.find(id="sourceAlias-coldRegistrationForm")['value'],
            'authType': '',
            'authToken': '',
            'key': ''

        })

        data = register_data.encode()
        response = request.urlopen("https://www.linkedin.com/reg/join-create", data)
        res_html = BeautifulSoup(response.read())
        Profile.dump_stuff('{}.html'.format('wtf'), str(res_html))

        pass

    def log_in(self):
        """
        Handle login. This should populate our cookie jar.
        """
        if self.is_logged_in():
            return

        req_html = request.urlopen("https://www.linkedin.com/uas/login").read()
        soup = BeautifulSoup(req_html)
        csrf = soup.find(id="loginCsrfParam-login")['value']

        login_data = parse.urlencode({
            'session_key': self.username,
            'session_password': self.password,
            'loginCsrfParam': csrf
        })

        data = login_data.encode()

        password_manager = request.HTTPPasswordMgrWithDefaultRealm()
        password_manager.add_password(None, "https://www.linkedin.com/", self.username, self.password)

        Registration.opener.add_handler(request.HTTPBasicAuthHandler(password_manager))

        response = request.urlopen("https://www.linkedin.com/uas/login-submit", data)
        res_html = BeautifulSoup(response.read())

        Registration.jar.save(Registration.cookie_filename)

        return response

    def is_logged_in(self):
        res = request.urlopen("https://www.linkedin.com/profile/view?id=" + str(self.profile_id))
        if res.geturl() == "https://www.linkedin.com/profile/view?id=" + str(self.profile_id):
            return True
        return False

