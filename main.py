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


class Crawler(object):
    everybody = {}
    cookie_filename = "cookies.txt"
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

        #res = self._login()
        #if res is None:
        #res = request.urlopen('http://www.linkedin.com/nhome/')

        #res = request.urlopen('http://www.linkedin.com/profile/view?id={}'.format(Crawler.root_id))
        #html = res.read()
        #soup = BeautifulSoup(html)

        #profile_v2 = soup.find_all('code', attrs={'id': 'profile_v2_guided_edit_promo-content'})[0]
        #profile_v2 = profile_v2.contents[0].replace(r'\u002d', '-')
        #profile_v2 = json.loads(profile_v2)

        #profiles = profile_v2['content']['Discovery']['discovery']['people']
        #for i in range(0, len(profiles)):
        #    profile = Profile(url = profiles[i]['link_profile'], profile_id=profiles[i]['memberID'])
        #    self._people_you_may_know_ids.append(profile.profile_id)
        #    self._people_you_may_know_urls.append(profile.url)
        #    self.people_you_may_know.append(profile)

        #profiles = profile_v2['content']['browse_map']['results']
        #for i in range(0, len(profiles)):
        #    profile = Profile(url=profiles[i]['pview'], profile_id=profiles[i]['memberID'])
        #    self._people_ids.append(profile.profile_id)
        #    self._people_urls.append(profile.url)
        #    self.people_also_viewed.append(profile)

        self.people_also_viewed = self.root_profile.people_also_viewed


    def _is_logged_in(self):
        res = request.urlopen("http://www.linkedin.com/profile/view?id=319955720")
        if res.geturl() == "http://www.linkedin.com/profile/view?id=319955720":
            return True
        return False

    def login_wtf(self):
        res = request.urlopen("https://www.linkedin.com/")

        html_code = res.read()
        soup = BeautifulSoup(html_code)
        form = soup.find(id='login')
        usernameinput = form.select('input[name=session_key]')[0]
        passwordinput = form.select('input[name=session_password]')[0]
        usernameinput['value'] = 'vanessa.kennedy.mccarthy@gmail.com'
        passwordinput['value'] = 'Password29'

        payload = dict((i['name'], i['value']) for i in form.find_all('input'))
        data = parse.urlencode(payload)
        #res.url or something
        loginrequest = res.Request(form['action'], data)
        loginresponse = res.urlopen(loginrequest)
        here = loginresponse.read()

    def _login(self):
        """
        Handle login. This should populate our cookie jar.
        """
        if self._is_logged_in():
            return

        login_data = parse.urlencode({
            'session_key': self.username,
            'session_password': self.password,
        })

        url = "https://www.linkedin.com/uas/login-submit"
        data = login_data.encode()

        response = request.urlopen(url, data)

        #people_also_viewed = soup('a', href=re.compile('^/profile/view'))
        #people_also_viewed = soup.select('.with-photo > a')
        #names = [x.find('img')['alt'] for x in people_also_viewed]
        #links = [urlparse(x['href']) for x in people_also_viewed]
        #ids = [parse_qs(x.query)['id'] for x in links]
        #thumbs =
        # [x.find('img')['data-li-src'] for x in people_also_viewed if x.find('img').attrs.has_key('data-li-src')]
        #profile = Profile(url, id = id, name = name, link = link)

        self.jar.save(self.cookie_filename)

        return response

    def run(self, levels):

        root = self.root_profile.people_also_viewed

        alive = []
        dead = []
        for x in root:
            dead.append(x)
        p = root[0]
        p._load_html()
        newp = None
        oldp = None
        #for i in range(0, levels):
        #    for x in dead:
        #        print('starting {}'.format(x.url))
        #        x._load_html()
        #        alive.extend(x.people_also_viewed)
        #
        #        print('\t {}'.format(x.name))
        #    dead = list(alive)
        #    alive = []

        for i in range(0, levels):

            print('starting {}'.format(p.url))

            print('\t {}'.format(p.name))

            who = random.randint(0, len(p.people_also_viewed) - 1)
            new_guy = p.people_also_viewed[who]
            print('\t considering {}'.format(new_guy.url))

            if new_guy.profile_id not in Profile.population_database:
                newp = new_guy
                newp._load_html()
            else:
                newp = Profile.population_database[new_guy.profile_id]
            if len(newp.people_also_viewed) == 0:
                continue

            p = newp


class Profile(object):
    population_database = {}

    def real_init(self, url):

        print('started creation of ' + self.url)

        res = request.urlopen(self.url)
        html = res.read()

        soup = BeautifulSoup(html)

        jsons = soup.find_all('code')

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
            raise Exception("What the fuck are you doing here? How could there be more json files?")

        self.name = self.json_profile_v1['content']['BasicInfo']['basic_info']['fullname']
        self.profile_id = self.json_profile_v1['content']['BasicInfo']['basic_info']['memberID']



        #try:
        #    self.first_name = soup.json_profile_v2['content']['Discovery']['discovery']['viewee']['firstName']
        #    self.last_name = soup.json_profile_v2['content']['Discovery']['discovery']['viewee']['lastName']
        #except TypeError as e:
        #    print('Can''t find first name and last name for {}'.format(self.name))

        #try:
        #    self.picture_src = self.json_profile_v2['content']['in_common']['viewee']['pictureID']
        #except (TypeError, KeyError) as e:
        #    print('Can''t find picture for {}'.format(self.name))
        #
        #assert self.html != ''

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

        self.population_database[self.profile_id] = self.url


    def _load_html(self):

        if self.html is not None:
            return

        res = request.urlopen(self.url)
        self.html = res.read()

        soup = BeautifulSoup(self.html)

        self.p2_message = self._get_json(soup, 'p2_message_exchanged')
        self.profile_v2 = self._get_json(soup, 'profile_v2_background')
        self.top_card = self._get_json(soup, 'top_card')
        self.profile_v2_guided_edit_promo = self._get_json(soup, 'profile_v2_guided_edit_promo')

        if self.profile_v2_guided_edit_promo is not None:
            self.profile_v2 = self.profile_v2_guided_edit_promo

        self._load_attributes()

        self._load_people_also_viewed()

    def _load_attributes(self):

        if self.p2_message is not None:
            self.first_name = self.p2_message['content']['discovery']['viewee']['firstName']
            self.last_name = self.p2_message['content']['discovery']['viewee']['lastName']
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
                self.dump_stuff('{}-top_card.json'.format(self.profile_id), json.dumps(self.top_card))
                self.name = self.profile_v2['content']['BasicInfo']['basic_info']['fullname']
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

    @staticmethod
    def _get_json(soup, name):
        dump = soup.find_all('code', attrs={'id': '{}-content'.format(name)})
        if len(dump) != 1:
            return
        dump = dump[0]
        dump = dump.contents[0].replace(r'\u002d', '-')
        return json.loads(dump)


    def _load_people_also_viewed(self):
        if self.has_people_also_viewed is not None:
            return

        try:
            if self.p2_message is not None:
                profiles = self.p2_message['content']['browse_map']['results']

            elif self.profile_v2 is not None:
                profiles = self.profile_v2['content']['browse_map']['results']

            elif self.top_card is not None:
                profiles = self.top_card['content']['browse_map']['results']

            else:
                raise Exception('what the fuck are you doing here')
        except KeyError as e:
            print('{} has no people also viewed'.format(self.name))
            self.has_people_also_viewed = False
            return

        for i in range(0, len(profiles)):
            url = profiles[i]['pview']
            name = profiles[i]['fullname']
            self.people_also_viewed.append(Profile(url=url, name=name))

        self.has_people_also_viewed = True
        return

    @staticmethod
    def dump_stuff(filename, txt):

        directory = os.getcwd() #os.path.dirname(filename)

        with open(directory + '\\json files\\' + filename, "w+") as text_file:
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

