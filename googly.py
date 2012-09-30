# -*- coding: utf-8 -*-
'''
Created on Mar 01, 2011

@author: Mourad Mourafiq

@copyright: Copyright © 2011

other contributers:
'''
from bs4 import BeautifulSoup
import cookielib
import os
import random
import time
import urllib
import urllib2
import urlparse

# Cookie jar. Stored at the user's home folder.
home_folder = os.getenv('HOME')
if not home_folder:
    home_folder = os.getenv('USERHOME')
    if not home_folder:
        home_folder = '.'   # Use the current folder on error.
cookie_jar = cookielib.LWPCookieJar(
                            os.path.join(home_folder, '.google-cookie'))
try:
    cookie_jar.load()
except Exception:
    pass


class GOOGLY(object):
    """
        Google object that executes queries and returns set of results
                
        URL templates to make Google searches.
            http://www.google.com/search?
            as_q=test (query string)
            &hl=en (language)
            &num=10 (number of results [10,20,30,50,100])
            &btnG=Google+Search
            &as_epq= (complete phrase)
            &as_oq= (at least one)
            &as_eq= (excluding)
            &lr= (language results. [lang_countrycode])
            &as_ft=i (filetype include or exclude. [i,e])
            &as_filetype= (filetype extension)
            &as_qdr=all (date [all,M3,m6,y])
            &as_nlo= (number range, low)
            &as_nhi= (number range, high)
            &as_occt=any (terms occur [any,title,body,url,links])
            &as_dt=i (restrict by domain [i,e])
            &as_sitesearch= (restrict by [site])
            &as_rights= (usage rights [cc_publicdomain, cc_attribute, cc_sharealike, cc_noncommercial, cc_nonderived]
            &safe=images (safesearch [safe=on,images=off])
            &as_rq= (similar pages)
            &as_lq= (pages that link)
            &gl=us (country)
    """
    def __init__(self, tld='com', hl='en', num=10, start=0, stop=None, pause=10.0, 
                 btnG="Google+Search", as_q=None, as_epq=None, as_oq=None, as_eq=None, 
                 lr=None, as_ft=None, as_filetype=None, as_qdr=all, as_nlo=None, as_nhi=None, 
                 as_occt=None, as_dt=None, as_sitesearch=None, as_rights=None, safe=None, 
                 as_rq=None, as_lq=None, gl="none"):
        self.as_q = as_q
        self.as_epq = as_epq        
        self.tld = tld
        self.hl = hl
        self.num = num
        self.start = start
        self.stop = stop
        self.pause = pause
        self.btnG = btnG
    
    def set_q(self, as_q):
        self.as_q = urllib.quote_plus(as_q)
    
    def set_epq(self, as_epq):
        self.as_epq = urllib.quote_plus(as_epq)
    
    def set_tld(self, tld):
        self.tld = tld
    
    def set_hl(self, hl):
        self.hl = hl

    def set_num(self, num):
        self.num = num

    def set_start(self, start):
        self.start = start
    
    def set_stop(self, stop):
        self.stop = stop

    def set_pause(self, pause):
        self.pause = pause    
    
    def __url_contruction(self, home=False):
        """
        Construct the search url depending on the parameters
        """        
        url_search = "http://www.google.%(tld)s/" % {"tld":self.tld}
        if home: return url_search
        
        url_search += "search?"        
        #language
        hl = "hl=%(hl)s&" % {"hl":self.hl}     
        url_search += hl
        if self.as_epq:
            as_epq = "as_epq=%(as_epq)s&" % {"as_epq":self.as_epq}     
            url_search += as_epq            
        elif self.as_q:
            as_q = "q=%(as_q)s&" % {"as_q":self.as_q}     
            url_search += as_q                        
        #num
        if self.num:
            num = "num=%(num)s&" % {"num":self.num}     
            url_search += num            
        if self.start:
            #start
            start = "start=%(start)s&" % {"start":self.start}     
            url_search += start
        else:
            btnG = "btnG=%(btnG)s&" % {"btnG":self.btnG}     
            url_search += btnG
                    
        return url_search        
        
    # Returns a generator that yields URLs.
    def search(self):
        """
        Returns search results for the current query as a iterator.
            as_q : the query we are looking for
            The as_eq parameter identifies a word or phrase that should not appear in any documents in the search results.      
        """            
        # pause, so as to not overburden google
        time.sleep(self.pause+(random.random()-0.5)*5)                
    
        home_url = self.__url_contruction(home=True)
        # Grab the cookie from the home page.
        self.__get_page(home_url)
    
        # Prepare the URL of the first request.
        url_search = self.__url_contruction()
        # Request the Google Search results page.
        html = self.__get_page(url_search)
    
        # Parse the response and extract the summaries
        soup = BeautifulSoup(html)
        return soup.findAll("div", {"class": "s"})
        
    # Request the given URL and return the response page, using the cookie jar.
    def __get_page(self, url):
        """
        Request the given URL and return the response page, using the cookie jar.
    
        @type  url: str
        @param url: URL to retrieve.
    
        @rtype:  str
        @return: Web page retrieved for the given URL.
    
        @raise IOError: An exception is raised on error.
        @raise urllib2.URLError: An exception is raised on error.
        @raise urllib2.HTTPError: An exception is raised on error.
        """
        request = urllib2.Request(url)
        request.add_header('User-Agent',
                           'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0)')
        cookie_jar.add_cookie_header(request)
        response = urllib2.urlopen(request)
        cookie_jar.extract_cookies(response, request)
        html = response.read()
        response.close()
        cookie_jar.save()
        return html

    
# When run as a script, take all arguments as a search query and run it.
if __name__ == "__main__":    
    query = 'google'
    google = GOOGLY()
    google.set_q(query)        
    if query:
        for url in google.search():
            print(url)
