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

class Crawler(object):

    everybody = {}
    cookie_filename = "cookies.txt"
    username = 'vanessa.kennedy.mccarthy@gmail.com'
    password = 'Password29'

    people_you_may_know = []

    def create_opener(self):

        password_manager = request.HTTPPasswordMgrWithDefaultRealm()
        password_manager.add_password(None, "https://www.linkedin.com/", self.username, self.password)

        opener = request.build_opener(request.HTTPCookieProcessor(self.jar),
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


    def _load_cookies(self):
        if os.access(self.cookie_filename, os.F_OK):
            self.jar.load(self.cookie_filename)
            return True
        return False


    def real_init(self):
        self.profiles = None
        self.soup = None                                        # Beautiful Soup object
        self.current_page = "https://www.linkedin.com/"          # Current page's address
        self.links = set()                             # Queue with every links fetched
        self.visited_links = set()

        self.counter = 0  # Simple counter for debug purpose

        self._load_cookies()

        res = self._login()

        if res is None:
            res = request.urlopen('http://www.linkedin.com/nhome/')

        html = res.read()

        self.soup = BeautifulSoup(html)

        #profiles = self.soup.select('.profile-summary')

        #urls = [x.find('a')['href'] for x in profiles]
        #names = [x.find('a').contents[0].strip() for x in profiles]
        #profile_ids = [parse_qs(urlparse(x).query)['id'] for x in urls]

        #for i in range(0, len(profiles)):
        #    url = urls[i]

            #profile = Profile(url)
            #self.people_you_may_know.append(profile)

    def __init__(self):
        self.jar = cookiejar.MozillaCookieJar(self.cookie_filename)

        self.create_opener()







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

    def run(self):

        #print "Currently have %d cookies" % len(self.jar)
        #print "Getting page"

        # Crawl 3 webpages (or stop if all url has been fetched)
        #while len(self.visited_links) < 3 or (self.visited_links == self.links):
        #    self.open()

        #for link in self.links:
        #    print link

        #print "Currently have %d cookies" % len(self.jar)
        #print self.jar

        for i in range(0, 2):
            self.people_you_may_know[i].harvest_profile()

        for x in range(0, 2):
            for y in range(0, 9):
                self.people_you_may_know[x].people_also_viewed[y].harvest_profile()

#need create profile constructor from url

class Profile(object):

    population_database= {}


    #url = None
    #profile_id = 0
    #picture_src = ''
    #
    #people_also_viewed = []
    #
    #html = ''
    #loaded = False
    #
    #name = ''
    #first_name = ''
    #last_name = ''
    #
    #json_profile_v1_str = ''
    #json_profile_v2_str = ''
    #json_profile_v3_str = ''
    #
    #json_profile_v1 = None
    #json_profile_v2 = None
    #json_profile_v3 = None
    #
    #is_stub = True

    def __init__(self, url):

        if self.is_absolute_url(url):
            self.url = url
        else:
            self.url = self.get_absolute_url(url)

        print('started creation of ' + self.url)

        #self.profile_id = kwargs.pop('profile_id', 0)
        #self.thumb_src = kwargs.pop('thumb_src', '')
        #self.image_src = kwargs.pop('image_src', '')
        #self.name = kwargs.pop('name', '')
        #self.html = kwargs.pop('html', '')
        #self.people_also_viewed = kwargs.pop('people_also_viewed', [])


        #if self.profile_id != 0: #necessary?
        #    return

        res = request.urlopen(self.url)
        self.html = res.read()

        soup = BeautifulSoup(self.html)


        jsons = soup.find_all('code')

        if len(jsons) == 2:
            self.json_profile_v1_str = jsons[0].contents[0]
            self.json_profile_v2_str = jsons[1].contents[0]

            self.json_profile_v1 = json.loads(self.json_profile_v1_str.replace(r'\u002d', '-'))
            self.json_profile_v2 = json.loads(self.json_profile_v2_str.replace(r'\u002d', '-'))

            try:
                self.first_name = self.json_profile_v2['content']['Discovery']['discovery']['viewee']['firstName']
                self.last_name = self.json_profile_v2['content']['Discovery']['discovery']['viewee']['lastName']
            except TypeError as e:
                print('\t no first name and last name for {}'.format(self.url))

            try:
                self.picture_src = self.json_profile_v2['content']['in_common']['viewee']['pictureID']
            except KeyError as e:
                print('\t no photo for {}'.format(self.url))


#started creation of http://www.linkedin.com/profile/view?id=128013505&authType=name&authToken=6gNW
#Traceback (most recent call last):
#  File "<console>", line 1, in <module>
#  File "E:\Users\Andrew\PycharmProjects\web_scraper\main.py", line 219, in run
#    self.people_you_may_know[i].harvest_profile()
#  File "E:\Users\Andrew\PycharmProjects\web_scraper\main.py", line 388, in harvest_profile
#    print('from ' + self.name)
#  File "E:\Users\Andrew\PycharmProjects\web_scraper\main.py", line 288, in __init__
#    self.first_name = self.json_profile_v2['content']['Discovery']['discovery']['viewee']['firstName']
#KeyError: 'viewee'

        elif len(jsons) == 3:
            self.json_profile_v1_str = jsons[0].contents[0]
            self.json_profile_v2_str = jsons[1].contents[0]
            self.json_profile_v3_str = jsons[2].contents[0]

            self.json_profile_v1 = json.loads(self.json_profile_v1_str.replace(r'\u002d', '-'))
            self.json_profile_v2 = json.loads(self.json_profile_v2_str.replace(r'\u002d', '-'))
            self.json_profile_v3 = json.loads(self.json_profile_v3_str.replace(r'\u002d', '-'))


            self.first_name = self.json_profile_v3['content']['Discovery']['discovery']['viewee']['firstName']
            self.last_name = self.json_profile_v3['content']['Discovery']['discovery']['viewee']['lastName']

            try:
                self.picture_src = self.json_profile_v3['content']['in_common']['viewee']['pictureID']
            except KeyError as e:
                print('\t no photo for {}'.format(self.url))
        elif len(jsons) == 1:
            self.json_profile_v1_str = jsons[0].contents[0]
            self.json_profile_v1 = json.loads(self.json_profile_v1_str.replace(r'\u002d', '-'))

            try:
                self.first_name = self.json_profile_v1['content']['Discovery']['discovery']['viewee']['firstName']
                self.last_name = self.json_profile_v1['content']['Discovery']['discovery']['viewee']['lastName']
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

        self.is_stub = False

    def _get_shit_from_html(self, soup):

        pass





    def harvest_profile(self):

        print('starting to harvest {0}s profile'.format(self.name))

        #soup = BeautifulSoup(self.html)
        #profiles = soup.select('.with-photo > a')


        if self.json_profile_v3_str != '':
            profiles = self.json_profile_v3['content']['browse_map']['results']
        else:
            profiles = self.json_profile_v2['content']['browse_map']['results']

        assert len(profiles) == 10

        names = [x['fullname'] for x in profiles]
        urls = [x['pview'] for x in profiles]
        profile_ids = [x['memberID'] for x in profiles]

        #names = [x.find('img')['alt'] for x in profiles]
        #urls = [x['href'] for x in profiles]
        #profile_ids = [parse_qs(urlparse(x.query))['id'][0] for x in urls]

        for i in range(0, len(profiles)):
            print('from ' + self.name)
            name = names[i]
            print('\t' + name)
            url = urls[i]
            print('\t' + url)
            profile_id = profile_ids[i]
            print('\t {}'.format(profile_id))
            print('\t {0} harvested from {1}s profile'.format(name, self.name))

            self.people_also_viewed.append(Profile(url))

        print('finished harvesting {0}s profile'.format(self.name))


    def dump_html(self):
        filename = '{}.html'.format(self.profile_id)
        directory = os.path.dirname(filename)

        with open(directory, "w") as text_file:
            text_file.write(self.html)

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

    #def __init__(self, link='', profile_id=0, thumb_src='', image_src='', name='', people_also_viewed=[]):
    #    self.link = link
    #    self.profile_id = profile_id
    #    self.thumb_src = thumb_src
    #    self.image_src = image_src
    #    self.name = name
    #    self.people_also_viewed = people_also_viewed


if __name__ == '__main__':

    c = Crawler()
    c.run()


def test_shit():

    pass