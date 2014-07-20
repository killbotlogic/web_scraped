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


class Profile(object):
    population_database = {}

    def real_init(self):

        print('started creation of ' + self.url)

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
        self.related_profile_ids = {}
        self.related_profiles = {}
        self.has_people_also_viewed = None
        self.html = None
        self.first_name = None
        self.last_name = None

        if Profile.is_absolute_url(url):
            self.url = url
        else:
            self.url = Profile.get_absolute_url(url)

        if profile_id == 0:
            self.profile_id = Profile.get_user_id(self.url)

        res = request.urlopen(self.url)
        html = res.read()
        self.soup = BeautifulSoup(html)

        if name == '':
            self.name = Profile.get_full_name(self.soup)

    def _load_html(self):

        if self.html is not None:
            return

        res = request.urlopen(self.url)
        self.html = res.read()

        soup = BeautifulSoup(self.html)

        # if (soup.find_all('code').__len__() =)

        cookies_disabled = soup.find_all('div', attrs={'id': 'cookieDisabled'})
        if len(cookies_disabled) > 0:
            raise Exception(cookies_disabled[0].text)

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
        # profiles = self.p2_message['content']['browse_map']['results']
        # elif self.profile_v2_guided_edit_promo is not None:
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

        directory = os.getcwd()  # os.path.dirname(filename)

        with open(directory + '\\debug_files\\' + filename, "w+", encoding='utf-8') as text_file:
            text_file.write(txt)

    @staticmethod
    def get_absolute_url(url):
        return 'https://www.linkedin.com' + url

    @staticmethod
    def get_full_size_picture_url(url):
        return 'http://m.c.lnkd.licdn.com/media' + url

    @staticmethod
    def is_absolute_url(url):
        return bool(urlparse(url).scheme)

    @staticmethod
    def get_user_id(url):
        return int(parse_qs(urlparse(url).query)['id'][0])

    @staticmethod
    def get_full_name(soup):
        title = soup.find('title').string
        title = title.split('|')[0]
        title = title.strip()
        return title

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


