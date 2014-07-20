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
            return Crawler.opener

        password_manager = request.HTTPPasswordMgrWithDefaultRealm()
        password_manager.add_password(None, "https://www.linkedin.com/", Crawler.username, Crawler.password)

        opener = request.build_opener(request.HTTPCookieProcessor(Crawler.jar),
                                      request.HTTPRedirectHandler(),
                                      request.HTTPHandler(debuglevel=0),
                                      request.HTTPSHandler(debuglevel=0),
                                      request.HTTPBasicAuthHandler(password_manager))

        #opener.addheaders = [('User-agent', 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2; .NET CLR 1.1.4322)')]
        opener.addheaders = [('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')]
        opener.addheaders = [('Accept-Encoding', 'gzip, deflate')]
        opener.addheaders = [('Accept-Language', 'en-US,en;q=0.5')]
        opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:26.0) Gecko/20100101 Firefox/26.0')]
        request.install_opener(opener)
        return opener

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

        self.soup = None                                        # Beautiful Soup object
        self.links = set()                             # Queue with every links fetched
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

        self.people_also_viewed = self.root_profile.people_also_viewed


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

class Profile(object):
    population_database = {}

    def real_init(self, url):

        print('started creation of ' + self.url)

        res = request.urlopen(self.url)
        html = res.read()

        self.soup = BeautifulSoup(html)

        jsons = self.soup.find_all('code')

        if len(jsons) == 2:

            try:
                pass
            except TypeError as e:
                print('\t no first name and last name for {}'.format(self.url))

            try:
                self.picture_src = self.json_profile_v2['content']['in_common']['viewee']['pictureID']
            except KeyError as e:
                print('\t no photo for {}'.format(self.url))

        elif len(jsons) == 3:
            self.json_profile_v1_str = jsons[0].contents[0]
            self.json_profile_v2_str = jsons[1].contents[0]
            self.json_profile_v3_str = jsons[2].contents[0]

            self.json_profile_v1 = json.loads(self.json_profile_v1_str.replace(r'\u002d', '-'))
            self.json_profile_v2 = json.loads(self.json_profile_v2_str.replace(r'\u002d', '-'))
            self.json_profile_v3 = json.loads(self.json_profile_v3_str.replace(r'\u002d', '-'))

            try:
                self.picture_src = self.json_profile_v3['content']['in_common']['viewee']['pictureID']
            except KeyError as e:
                print('\t no photo for {}'.format(self.url))
        elif len(jsons) == 1:
            self.json_profile_v1_str = jsons[0].contents[0]
            self.json_profile_v1 = json.loads(self.json_profile_v1_str.replace(r'\u002d', '-'))

            try:
                pass
            except TypeError as e:
                print('\t no first name and last name for {}'.format(self.url))

            try:
                self.picture_src = self.json_profile_v1['content']['in_common']['viewee']['pictureID']
            except KeyError as e:
                print('\t no photo for {}'.format(self.url))

        else:
            raise Exception("What the fuck are you doing here? How could there be more debug_files?")

        self.name = self.json_profile_v1['content']['BasicInfo']['basic_info']['fullname']
        self.profile_id = self.json_profile_v1['content']['BasicInfo']['basic_info']['memberID']

        print('\t created ' + self.name)


    def __init__(self, url='', profile_id=0, thumb_src='', image_src='', name=''):

        self.profile_id = profile_id
        self.thumb_src = thumb_src
        self.image_src = image_src
        self.name = name
        self.people_also_viewed = []
        self.has_people_also_viewed = None
        self.html = None
        self.first_name = None
        self.last_name = None

        if self.is_absolute_url(url):
            self.url = url
        else:
            self.url = self.get_absolute_url(url)

        if self.profile_id == 0:
            self.profile_id = int(parse_qs(urlparse(self.url).query)['id'][0])


    def _load_html(self):

        if self.html is not None:
            return

        res = request.urlopen(self.url)
        self.html = res.read()

        soup = BeautifulSoup(self.html)

        # if (soup.find_all('code').__len__() =)

        cookieDisabled = soup.find_all('div', attrs={'id': 'cookieDisabled'})
        if len(cookieDisabled) > 0:
            raise Exception(cookieDisabled[0].text)

        self.p2_message = self._get_json(soup, 'p2_message_exchanged')
        self.profile_v2 = self._get_json(soup, 'profile_v2_background')
        self.top_card = self._get_json(soup, 'top_card')
        self.profile_v2_guided_edit_promo = self._get_json(soup, 'profile_v2_guided_edit_promo')

        # if self.profile_v2_guided_edit_promo is not None:
        # self.profile_v2 = self.profile_v2_guided_edit_promo

        self._load_attributes()

        self._load_profile_links()

        self.population_database[self.profile_id] = self

    def _load_attributes(self):

        if self.p2_message is not None:
            self.first_name = self.p2_message['content']['discovery']['viewee']['firstName']
            self.last_name = self.p2_message['content']['discovery']['viewee']['lastName']
            return

        if self.profile_v2_guided_edit_promo is not None:
            try:
                self.first_name = self.profile_v2_guided_edit_promo['content']['discovery']['viewee']['firstName']
                self.last_name = self.profile_v2_guided_edit_promo['content']['discovery']['viewee']['lastName']
                return
            except KeyError as e:
                print(e.__str__)
                print('Cannot find name for {}'.format(self.url))
                self.dump_stuff('{}-profile_v2_guided_edit_promo.json'.format(self.profile_id),
                                json.dumps(self.profile_v2_guided_edit_promo))
                self.name = self.profile_v2_guided_edit_promo['content']['BasicInfo']['basic_info']['fullname']
                return

        if self.top_card is not None:
            try:
                self.first_name = self.top_card['content']['discovery']['viewee']['firstName']
                self.last_name = self.top_card['content']['discovery']['viewee']['lastName']
                return
            except KeyError as e:
                print(e.__str__)
                print('Cannot find name for {}'.format(self.url))
                self.dump_stuff('{}-top_card.json'.format(self.profile_id), json.dumps(self.top_card))
                self.name = self.top_card['content']['BasicInfo']['basic_info']['fullname']
                return

        if self.profile_v2 is not None:
            try:
                self.first_name = self.profile_v2['content']['discovery']['viewee']['firstName']
                self.last_name = self.profile_v2['content']['discovery']['viewee']['lastName']
                return
            except KeyError as e:
                print(e.__str__)
                print('Cannot find name for {}'.format(self.url))
                self.dump_stuff('{}-profile_v2.json'.format(self.profile_id), json.dumps(self.profile_v2))
                self.name = self.profile_v2['content']['BasicInfo']['basic_info']['fullname']
                return


    @staticmethod
    def _get_json(soup, name):
        dump = soup.find_all('code', attrs={'id': '{}-content'.format(name)})
        if len(dump) != 1:
            return
        dump = dump[0]
        dump = dump.contents[0].replace(r'\u002d', '-')
        return json.loads(dump)


    def _load_profile_links(self):
        if self.has_people_also_viewed is not None:
            return

        # try:
        # if self.p2_message is not None:
        #         profiles = self.p2_message['content']['browse_map']['results']
        #     elif self.profile_v2_guided_edit_promo is not None:
        #         profiles = self.profile_v2_guided_edit_promo['content']['browse_map']['results']
        #     elif self.profile_v2 is not None:
        #         profiles = self.profile_v2['content']['browse_map']['results']
        #     elif self.top_card is not None:
        #         profiles = self.top_card['content']['browse_map']['results']
        #     else:
        #         # raise Exception('what the fuck are you doing here')
        #         print('{} has no fucking json to parse'.format(self.name))
        #         profiles = []
        # except KeyError as e:
        #     print('{} has no people also viewed'.format(self.name))
        #     self.has_people_also_viewed = False
        #     return

        profiles = []

        for i in range(0, len(profiles)):
            url = profiles[i]['pview']
            name = profiles[i]['fullname']
            self.people_also_viewed.append(Profile(url=url, name=name))

        self.has_people_also_viewed = True
        return

    @staticmethod
    def dump_stuff(filename, txt):

        directory = os.getcwd() #os.path.dirname(filename)

        with open(directory + '\\debug_files\\' + filename, "w+", encoding='utf-8') as text_file:
            text_file.write(txt)

            #if not os.path.exists(dir):
            #        os.makedirs(dir)


    @staticmethod
    def get_absolute_url(url):
        return 'https://www.linkedin.com' + url

    @staticmethod
    def get_full_size_picture_url(url):
        return 'http://m.c.lnkd.licdn.com/media' + url

    @staticmethod
    def is_absolute_url(url):
        return bool(urlparse(url).scheme)


    def __str__(self):
        return 'Name: {}, Url: {}'.format(self.name, self.url)

    def __cmp__(self, other):
        if self.profile_id > other.profile_id:
            return 1
        elif self.profile_id < other.profile_id:
            return -1
        else:
            return 0

    def __hash__(self):
        return self.profile_id

    def __eq__(self, other):
        return self.profile_id == other.profile_id


if __name__ == '__main__':
    c = Crawler()
    c.run()

