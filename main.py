from bs4 import BeautifulSoup
import urllib
import urllib2
import itertools
import random
import cookielib
import os
from urllib2 import HTTPError


class Crawler(object):

    cookie_filename = "cookies.txt"
    username = 'vanessa.kennedy.mccarthy@gmail.com'
    password = 'Password29'

    def create_opener(self):
        jar = cookielib.MozillaCookieJar(self.cookie_filename)

        if os.access(self.cookie_filename, os.F_OK):
                jar.load()

        password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_manager.add_password(None, "https://www.linkedin.com/", self.username, self.password)

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar),
                                      urllib2.HTTPRedirectHandler(),
                                      urllib2.HTTPHandler(debuglevel=0),
                                      urllib2.HTTPSHandler(debuglevel=0),
                                      urllib2.HTTPBasicAuthHandler(password_manager))

        opener.addheaders = [('User-agent', ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2; .NET CLR 1.1.4322)'))]
        urllib2.install_opener(opener)
        return opener

    def __init__(self):

        self.profiles = None
        self.soup = None                                        # Beautiful Soup object
        self.current_page = "https://www.linkedin.com/"          # Current page's address
        self.links = set()                             # Queue with every links fetched
        self.visited_links = set()

        self.counter = 0  # Simple counter for debug purpose

        self.opener = self.create_opener()

        self.login_page()

    def login_wtf(self):
        """
            isJsEnabled

            source_app

            session_key = 'vanessa.kennedy.mccarthy@gmail.com'

            session_password = 'Password29'

            signin

            session_redirect

            trk

            loginCsrfParam

            csrfToken

            sourceAlias
        """
        request = self.opener.open("https://www.linkedin.com/")

        html_code = request.read()
        soup = BeautifulSoup(html_code)
        form = soup.find(id='login')
        usernameinput = form.select('input[name=session_key]')[0]
        passwordinput = form.select('input[name=session_password]')[0]
        usernameinput['value'] = 'vanessa.kennedy.mccarthy@gmail.com'
        passwordinput['value'] = 'Password29'


        payload = dict((i['name'], i['value']) for i in form.find_all('input'))
        data = urllib.urlencode(payload)
        #res.url or something
        loginrequest = urllib2.Request(form['action'], data)
        loginresponse = urllib2.urlopen(loginrequest)
        here = loginresponse.read()

    def load_page(self, url, data=None):
        """
        Utility function to load HTML from URLs for us with hack to continue despite 404
        """
        # We'll print the url in case of infinite loop
        # print "Loading URL: %s" % url
        try:
            if data is not None:
                response = self.opener.open(url, data)
            else:
                response = self.opener.open(url)
            return response
                #''.join(response.readlines())
        except HTTPError as e:
            # If URL doesn't load for ANY reason, try again...
            # Quick and dirty solution for 404 returns because of network problems
            # However, this could infinite loop if there's an actual problem
            raise e
            #return self.loadPage(url, data)

    def login_page(self):
        """
        Handle login. This should populate our cookie jar.
        """
        login_data = urllib.urlencode({
            'session_key': self.username,
            'session_password': self.password,
        })

        response = self.load_page("https://www.linkedin.com/uas/login-submit", login_data)

        assert response.geturl() == 'http://www.linkedin.com/nhome/'
        html = response.read()
        self.soup = BeautifulSoup(html)

        self.profiles = self.soup.select('.profile-summary')
        #profiles[0].find_all('a')[0].contents[0].strip()
        #people_you_may_know = [x.find('a').contents[0].strip() for x in c.profiles]
        #people_you_may_know = [x.find('a')['href'] for x in c.profiles]
        return response

    def load_title(self):
        html = self.load_page("http://www.linkedin.com/nhome")
        soup = BeautifulSoup(html)
        return soup.find("title")

    def open(self):

        # Open url
        print self.counter, ":", self.current_page
        try:
            res = self.opener.open(self.current_page)
        except HTTPError as e:
            print "HTTPError probably 404"
            raise e
        print res.headers
        print "Got page"

        html_code = res.read()
        self.visited_links.add(self.current_page) 

        # Fetch every links
        self.soup = BeautifulSoup(html_code)

        page_links = []

        shitty_links = self.soup.findAll('a')
        #try :
        good_links = itertools.ifilter(lambda href: 'http://' in href or '', (a.get('href') for a in shitty_links))
        #except Exception: # Magnificent exception handling
        #    pass

        # Update links 
        self.links = self.links.union(set(good_links))

        # Choose a random url from non-visited set
        self.current_page = random.sample( self.links.difference(self.visited_links),1)[0]
        self.counter+=1

    def run(self):

        print "Currently have %d cookies" % len(self.jar)
        print "Getting page"

        # Crawl 3 webpages (or stop if all url has been fetched)
        while len(self.visited_links) < 3 or (self.visited_links == self.links):
            self.open()

        for link in self.links:
            print link

        print "Currently have %d cookies" % len(self.jar)
        print self.jar

if __name__ == '__main__':

    C = Crawler()
    #C.run()