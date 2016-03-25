from ..search import SearchRequest
import string
import urllib
from urlparse import urlparse
from collections import defaultdict
import re


def _format_keywords(kwords):
    #Multiple keywords are concatenated with + sign - translate both to the simple space
    kwords = kwords.replace("+", " ")
    return kwords

def _format_multi_param(param_str):

    vals = param_str.split("|") #split by the separator
    vals = ['Not Specified' if i=='!' else i for i in vals] #! represents the code of "not specified ""

    return vals

def parse(url, name=None):

    """ Converts the content of url into search request object"""

    base_net_address, path, search_params = _parse_base_ebay_url(url)

    if not _is_valid_ebay_url_link(base_net_address):
        return None

    url_orig = url
    url = _url_special_char_decoding(url)

    #parse bookmarked URL
    l = url.split('?')[1].split('&') #skip address continue to the params
    l = map(lambda x: tuple(x.split('=')), l) #match key-value pairs
    l = [(i[0], "") if len(i)==1 else i for i in l] #expand short tuples 
    l = filter(lambda x: len(x)==2, l) #remove invalid multiples (triples etc.)

    d_url = {} 
    d_url.update(l) #update dict with list of tuples
    

    # ****************************
    # CREATE SEARCH REQUEST
    # ****************************

    #Convert to attributes of search instance
    sinstance = SearchRequest(id_= url_orig)

    #save the url of the search
    sinstance['url'] = url_orig

    #custom name of this search request
    if name: sinstance['name']= name

    # ****************************
    # KEYWORD RESOLUTION
    # ****************************

    if '_nkw' in d_url:
        sinstance['keywords'] = _format_keywords(d_url['_nkw'])


    # ****************************
    # CATEGORY RESOLUTION
    # ****************************

    cat = None #denotes no category set

    if '_sacat' in d_url:
        cat = d_url['_sacat']

    else:
        #Try to extract category info from the url - ugly but effective
        m = re.split("^http://www.ebay\..+/sch/"+"(.*?)"+"\?"+"(.*?)", url)

        if len(m)>=2:
            m = m[1] #returns the first portion of url (before ? sign) 
            m = filter(lambda x: x.isdigit(), m.split('/') )#split with / char and keep only numerics

            if len(m)>0: 
                cat = m[0]

    if cat and int(cat)>0: #cat is set to zero when seller is specified (search is performed accross all categories)
        sinstance['categoryId']= cat


    # ****************************
    # SELLER RESOLUTION
    # ****************************

    if 'categoryId' not in sinstance and 'keywords' not in sinstance:
        #TODO parse url when search was performed for the specific seller only
        #E.g. http://www.ebay.co.uk/sch/fashionablebargains/m.html?_ipg=48&_sop=12&_rdc=1
        #Note: if either category or keywords have been set, then url would have a different format (and seller id would be specified in _ssn parameter)
        s = re.split('^http://www.ebay\..+/sch/', url)
        if len(s)>=2:
            sinstance['Seller'] =  s[1].split('/')[0]

    # ****************************
    # DOMAIN RESOLUTION
    # ****************************

    domain_extractor = lambda url: [i for i in url.split('/') if 'ebay' in i][0]
    sinstance['site']= domain_extractor(url)

    if 'LH_PrefLoc' in d_url: 
        sinstance['pref_location']= d_url['LH_PrefLoc'] #if 1 then it relates to the site (1==GB for co.uk, 1==US for .com)
        del d_url['LH_PrefLoc']

    if '.com' in sinstance['site'] and sinstance['pref_location']=='1':
        sinstance['LocatedIn']= 'US'

    elif '.co.uk' in sinstance['site'] and sinstance['pref_location']=='1':
        sinstance['LocatedIn']= 'GB'

    #Extract the domain: UK, US, DE etc
    domain_names = ['UK', 'US', 'DE', 'IT', 'FR', 'ES', 'AT', 'AU']
    domain_extensions = ['.co.uk', '.com', '.de', '.it', '.fr', '.es', '.at', '.com.au']

    ext = re.split("^http://"+"(.*?)"+".ebay"+"(.*?)"+"/"+"(.*?)", url)[2] #extract the extension from the url
    sinstance['domain'] = domain_names[domain_extensions.index(ext)] #match the extension to the name of the domain

    # ****************************
    # CONDITION RESOLUTION
    # ****************************

    #Some weird problem with condition codes in some URL's (typicall values: 1000 == New with tags, 3000 == Used etc)
    if 'LH_ItemCondition' in d_url:
        conds = _format_multi_param(d_url['LH_ItemCondition'])
        c_map = {'3': '1000', '4':'3000'} #values 3 and 4 represent New and Used items repectively, but not supported by ebay api
        sinstance['Condition']= map(lambda x: c_map[x] if x in c_map else x, conds)
        del d_url['LH_ItemCondition']

    # ****************************
    # SEARCH PARAMETERS RESOLUTION
    # ****************************

    # Set defaults:
    sinstance['ListingType']= 'All'
    sinstance['descriptionSearch'] = False
    
    #Single value params
    if '_udlo' in d_url:         sinstance['MinPrice']= d_url['_udlo']
    if '_udhi' in d_url:         sinstance['MaxPrice']= d_url['_udhi']

    if 'LH_TitleDesc' in d_url:  
        sinstance['descriptionSearch'] = True   #searching both the title and the description
        del d_url['LH_TitleDesc']

    if '_ssn' in d_url:          sinstance['Seller'] = d_url['_ssn']

    if   'LH_Auction' in d_url and d_url['LH_Auction'] =='1': 
        sinstance['ListingType']= 'Auction'
        del d_url['LH_Auction']

    elif 'LH_BIN' in d_url and d_url['LH_BIN'] =='1':       
        sinstance['ListingType']= 'FixedPrice'
        del d_url['LH_BIN']

    #Multiple value params (not prefixed with underscore and capitalized)
    d_url = {k: d_url[k] for k in filter(lambda x: x[0]!="_", d_url)}
    d_url = {k: d_url[k] for k in filter(lambda x: x[0]>="A" and x[0]<="Z", d_url)}

    for param in d_url:
        if param in sinstance: continue
        sinstance[param] = _format_multi_param(d_url[param])
        sinstance.addAspectFilter(param) # mark this parameter as product parameter

    return sinstance


def _is_valid_ebay_url_link(base_net_address):
    return ".ebay." not in base_net_address

def _url_special_char_decoding(url):

    """ Special url characterters decoding """

    url_decoded = url
    url_decoded_prev = ""

    try:
        #Multiple keywords are concatenated with either + sign or %20 string - translate both to the simple space
        while url_decoded != url_decoded_prev:
            url_decoded_prev = url_decoded
            url_decoded = urllib.unquote(url_decoded_prev).decode('utf8', errors = 'replace') 
    except UnicodeEncodeError:
        pass #TODO -- fails when using: http://www.ebay.co.uk/sch/Health-Beauty-/26395/i.html?LH_Auction=1&_from=R40&_sop=10&_nkw=brush&LH_PrefLoc=1&_dcat=82597&rt=nc&_pppn=r1&Brand=CHANEL%7CChristian%2520Dior%7CLanc%25C3%25B4me%7CNARS%7CYSL%252C%2520Yves%2520Saint%2520Laurent
    return url_decoded


def _parse_base_ebay_url(url_string):
    parse_result = urlparse(url_string)
    base_net_address = parse_result.netloc
    path = parse_result.path
    search_params = parse_result.query

    return base_net_address, path, search_params


""" ####################################### TESTS ################################################ """


from unittest import TestCase

class TestEbayUrl(TestCase):

    def test_simple_search_url(self):
        test_url1 = None

    def test_seller_search(self):
        test_url_with_seller_in_query = "http://www.ebay.co.uk/sch/m.html?_nkw=&_armrs=1&_ipg=&_from=&_ssn=*polkadots*&_sop=10"
        test_url_with_seller_in_path = "http://www.ebay.co.uk/sch/adey2571/m.html?_nkw=&_armrs=1&_ipg=&_from="

    def test_seller_search_with_params(self):
        test_url = "http://www.ebay.co.uk/sch/m.html?_nkw=&_armrs=1&_ipg=&_from=&_ssn=*polkadots*&_sop=10"

    def test_category_search(self):
        pass

    def test_special_char_encoding(self):
        test_url = ""
        _url_special_char_decoding(search_params)




