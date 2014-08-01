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
from faker import Faker
import time

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
        opener.addheaders = [('Accept-Encoding', 'gzip,deflate,sdch')]
        opener.addheaders = [('Accept-Language', 'en-US,en;q=0.8')]
        opener.addheaders = [('Cache-Control', 'en-US,en;q=0.8')]
        opener.addheaders = [('Cache-Control', 'max-age=0')]
        opener.addheaders = [('Connection', 'keep-alive')]
        # opener.addheaders = [('', '')]
        # opener.addheaders = [('', '')]
        # opener.addheaders = [('', '')]
        # opener.addheaders = [('', '')]
        # opener.addheaders = [('', '')]


        # Content-Length:249
        # Content-Type:application/x-www-form-urlencoded
        # Cookie:JSESSIONID="ajax:7097097261172758893"; visit="v=1&G"; bcookie="v=2&c07afefc-f040-498d-836f-ba2635ef5f8a"; bscookie="v=1&201408010539436f070b58-7482-45db-87b0-e110efac6bf4AQHGxg4rk9fSdRk2dG28shczD7K7VxIM"; lidc="b=LB05:g=72:u=1:i=1406871583:t=1406957983:s=1406961284"; L1e=19e93e8; __utma=23068709.1510226847.1406871587.1406871587.1406871587.1; __utmb=23068709.2.10.1406871587; __utmc=23068709; __utmz=23068709.1406871587.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmv=23068709.guest; __qca=P0-1101210924-1406871588001; leo_auth_token="GST:U16enO7-QqjwpRObpQ6eAFcb-6ovpLSb2m_z5RcJbjj-qaCiH970Ij:1406871629:93b6b6e4cff7be463c394a90c4435f65acc1ca98"; lang="v=2&lang=en-us"; RT=s=1406871632330&r=https%3A%2F%2Fwww.linkedin.com%2Freg%2Fjoin
        # Host:www.linkedin.com
        # Origin:https://www.linkedin.com
        # Referer:https://www.linkedin.com/reg/join

        opener.addheaders = [('User-Agent',
                              'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36')]
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
            self.username = self.faker.user_name() + '@killbotlogic.com'

        if password != '':
            self.password = password
        else:
            self.password = self.faker.password()

        if self.profile_id == 0:
            self.profile_id = 0


    def register(self):
        req_html = request.urlopen("https://www.linkedin.com/reg/join").read()

        soup = BeautifulSoup(req_html)

        register_data = parse.urlencode({
            'isJsEnabled': 'false',
            'firstName': self.first_name,
            'lastName': self.last_name,
            'email': self.username,
            'password': self.password,
            'csrfToken': soup.find(id="csrfToken-coldRegistrationForm")['value'],
            'sourceAlias': soup.find(id="sourceAlias-coldRegistrationForm")['value'],
            'webmailImport': 'false',
            'trcode': '',
            'genie-reg': '',
            'mod': '',
            'key': '',
            'authToken': '',
            'authType': ''
        })

        data = register_data.encode()

        time.sleep(10.3867)

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

