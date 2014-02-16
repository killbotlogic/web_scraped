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

    root_id = 319955720
    jar = cookiejar.MozillaCookieJar(cookie_filename)
    opener = None
    _cookies_loaded = False

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


    def real_init(self):

        self._load_cookies()
        self._login()


        self.profiles = None
        self.soup = None                                        # Beautiful Soup object
        self.current_page = "https://www.linkedin.com/"          # Current page's address
        self.links = set()                             # Queue with every links fetched
        self.visited_links = set()
        self._people_you_may_know_ids = []
        self._people_you_may_know_urls = []
        self.counter = 0  # Simple counter for debug purpose




        #res = self._login()
        #if res is None:
        #    res = request.urlopen('http://www.linkedin.com/nhome/')

        res = request.urlopen('http://www.linkedin.com/profile/view?id={}'.format(Crawler.root_id))
        html = res.read()
        soup = BeautifulSoup(html)

        profile_v2_guided_edit_promo = soup.find_all('code', attrs={'id':'profile_v2_guided_edit_promo-content'})[0]
        assert len(profile_v2_guided_edit_promo.contents) == 1
        profile_v2_guided_edit_promo = profile_v2_guided_edit_promo.contents[0].replace(r'\u002d', '-')
        profile_v2_guided_edit_promo = json.loads(profile_v2_guided_edit_promo)

        profiles = profile_v2_guided_edit_promo['content']['Discovery']['discovery']['people']
        for i in range(0, len(profiles)):
            profile = Profile(url = profiles[i]['link_profile'], profile_id=profiles[i]['memberID'])
            self._people_you_may_know_ids.append(profile.url)
            self._people_you_may_know_urls.append(profile.profile_id)
            self.people_you_may_know.append(profile)


        #profiles = self.soup.select('.profile-summary')

        #urls = [x.find('a')['href'] for x in profiles]


        #for i in range(0, len(profiles)):
        #    url = urls[i]
        #profile = Profile(url)
        #    self.people_you_may_know.append(member_id, profile)

    def __init__(self):
        self._create_opener()
        self._load_cookies()



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

        self.is_stub = False



    def __init__(self, url='', profile_id=0, thumb_src='', image_src='', name='', people_also_viewed=[]):
        self.url = url
        self.profile_id = profile_id
        self.thumb_src = thumb_src
        self.image_src = image_src
        self.name = name
        self.people_also_viewed = people_also_viewed

        if self.is_absolute_url(url):
            self.url = url
        else:
            self.url = self.get_absolute_url(url)

        if self.profile_id == 0:
          self.profile_id = int(parse_qs(urlparse(self.url).query)['id'][0])

        self.population_database[self.profile_id] = self.url

    def _get_shit_from_html(self):

        res = request.urlopen(self.url)
        html = res.read()

        self._soup = BeautifulSoup(html)



        self.v2_json = self._load_linked_in_json('profile_v2_background')

        if self.v2_json is not None:
            self.first_name = self.v2_json['content']['Discovery']['discovery']['viewee']['firstName']
            self.last_name = self.v2_json['content']['Discovery']['discovery']['viewee']['lastName']
            no_photo = True
            if no_photo:
                self.picture_src = self.v2_json['content']['in_common']['vieweePhoto']['ghost']
            else:
                pass
            self._load_people_also_viewed()



        self.top_card = self._load_linked_in_json('top_card')





        #profiles = profile_v2_background['content']['Discovery']['discovery']['people']
        #for i in range(0, len(profiles)):
        #    profile = Profile(url = profiles['link_profile'], profile_id= profiles['memberID'])
        #    self._people_you_may_know_ids.add(profile.url)
        #    self._people_you_may_know_urls.add(profile.profile_id)

    def _load_linked_in_json(self, name):
        the_load = self._soup.find_all('code', attrs={'id':'{}-content'.format(name)})[0]
        assert len(the_load.contents) == 1
        the_load = the_load.contents[0].replace(r'\u002d', '-')
        return json.loads(the_load)


    def _load_people_also_viewed(self):
        profiles = self.v2_json['content']['browse_map']['results']

        names = [x['fullname'] for x in profiles]
        urls = [x['pview'] for x in profiles]
        profile_ids = [x['memberID'] for x in profiles]

        for i in range(0, len(profiles)):
            print('from ' + self.name)
            print('\t' + names[i])
            print('\t' + urls[i])
            profile_id = profile_ids[i]
            print('\t {}'.format(profile_id))
            print('\t {0} harvested from {1}s profile'.format(names[i], self.name))
            self.people_also_viewed.append(Profile(url=urls[i]))


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




if __name__ == '__main__':

    c = Crawler()
    c.run()

