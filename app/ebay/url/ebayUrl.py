from ..search import SearchRequest
import string
from collections import defaultdict
import re


def _format_keywords(kwords):
    #Multiple keywords are concatenated with either + sign or %20 string - translate both to the simple space

    # tbl = string.maketrans('+', ' ') 
    # kwords_t = kwords.translate(tbl)
    kwords_t = kwords
    kwords_t = kwords_t.replace("+%28", "(")
    kwords_t = kwords_t.replace("%29", ")")
    kwords_t = kwords_t.replace("%2C+", ",")
    kwords_t = kwords_t.replace("+", " ")
    kwords_t = kwords_t.replace("%20", " ")
    
    return kwords_t

def _format_multi_param(param_str):

    vals = param_str.split("%7C") #split by the separator
    vals = [i.replace("%2520", " ") for i in vals] #space
    vals = ['Not Specified' if i=='%21' else i for i in vals] #not specified code

    return vals

def parse(url, name=None):

    """ Converts the content of url into search request object"""

    if ".ebay." not in url: 
        return  None #Non ebay link in ebay folder - skip it

    #parse bookmarked URL
    l = url.split('?')[1].split('&') #skip address continue to the params
    l = map(lambda x: tuple(x.split('=')), l) #match key-value pairs
    l = [(i[0], "") if len(i)==1 else i for i in l] #expand short tuples 
    
    d_url = {}#defaultdict(lambda: None)
    d_url.update(l) #update dict with list of tuples

    #Convert to attributes of search instance
    sinstance = SearchRequest(id_= url)

    #Format the keywords
    if '_nkw' in d_url:
        sinstance['keywords'] = _format_keywords(d_url['_nkw'])


    #Format the category
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

    if 'categoryId' not in sinstance and 'keywords' not in sinstance:
        #TODO parse url when search was performed for the specific seller only
        #E.g. http://www.ebay.co.uk/sch/fashionablebargains/m.html?_ipg=48&_sop=12&_rdc=1
        #Note: if either category or keywords have been set, then url would have a different format (and seller id would be specified in _ssn parameter)
        s = re.split('^http://www.ebay\..+/sch/', url)
        if len(s)>=2:
            sinstance['Seller'] =  s[1].split('/')[0]

    #Format other params
    site_extract = lambda url: [i for i in url.split('/') if 'ebay' in i][0]
    sinstance['site']= site_extract(url)

    #Item location
    if 'LH_PrefLoc' in d_url: sinstance['pref_location']= d_url['LH_PrefLoc'] #if 1 then it relates to the site (1==GB for co.uk, 1==US for .com

    if '.com' in sinstance['site'] and sinstance['pref_location']=='1':
        sinstance['LocatedIn']= 'US'

    elif '.co.uk' in sinstance['site'] and sinstance['pref_location']=='1':
        sinstance['LocatedIn']= 'GB'
    #TODO the rest
    
    #Single value params
    if '_udlo' in d_url:         sinstance['MinPrice']= d_url['_udlo']
    if '_udhi' in d_url:         sinstance['MaxPrice']= d_url['_udhi']
    if 'LH_TitleDesc' in d_url:  sinstance['descriptionSearch'] = True   #searching both the title and the description
    else:                        sinstance['descriptionSearch'] = False
    if '_ssn' in d_url:          sinstance['Seller'] = d_url['_ssn']

    if 'LH_Auction' in d_url and d_url['LH_Auction'] =='1': sinstance['ListingType']= 'Auction'
    elif 'LH_BIN' in d_url and d_url['LH_BIN'] =='1':       sinstance['ListingType']= 'FixedPrice'
    else:                                                   sinstance['ListingType']= 'All'

    #Multiple value params
    if 'Size' in d_url:                    sinstance['Size']        = _format_multi_param(d_url['Size'])
    if 'Shoe%2520Size' in d_url:           sinstance['Shoe Size']   = _format_multi_param(d_url['Shoe%2520Size'])
    if 'Trouser%2520Size' in d_url:        sinstance['Trouser Size']= _format_multi_param(d_url['Trouser%2520Size'])
    if 'Cup%2520Size' in d_url:            sinstance['Cup Size']    = _format_multi_param(d_url['Cup%2520Size'])
    if 'Chest%2520Size' in d_url:          sinstance['Chest Size']  = _format_multi_param(d_url['Chest%2520Size'])
    if 'Brand' in d_url:                   sinstance['Brand']       = _format_multi_param(d_url['Brand'])
    if 'Material' in d_url:                sinstance['Material']    = _format_multi_param(d_url['Material'])
    if 'Main%2520Colour' in d_url:         sinstance['Main Colour']  = _format_multi_param(d_url['Main%2520Colour'])
    if 'Color' in d_url:                   sinstance['Color']       = _format_multi_param(d_url['Color'])
    if 'Metal' in d_url:                   sinstance['Metal']       = _format_multi_param(d_url['Metal'])
    if 'Material' in d_url:                sinstance['Material']    = _format_multi_param(d_url['Material'])
    if 'Style' in d_url:                   sinstance['Style']       = _format_multi_param(d_url['Style'])
    if 'Main%2520Stone' in d_url:          sinstance['Main Stone']  = _format_multi_param(d_url['Main%2520Stone'])
    if 'Length' in d_url:                  sinstance['Length']      = _format_multi_param(d_url['Length'])

    #Some weird problem with conditon codes in some URL's (typicall values: 1000 == New with tags, 3000 == Used etc)
    if 'LH_ItemCondition' in d_url:
        conds = _format_multi_param(d_url['LH_ItemCondition'])
        c_map = {'3': '1000', '4':'3000'} #values 3 and 4 represent New and Used items repectively, but not supported by ebay api
        sinstance['Condition']= map(lambda x: c_map[x] if x in c_map else x, conds)
    
    #save the url of the search
    sinstance['url'] = url

    #Extract the domain: UK, US, DE etc
    domain_names = ['UK', 'US', 'DE', 'IT', 'FR', 'ES', 'AT', 'AU']
    domain_extensions = ['.co.uk', '.com', '.de', '.it', '.fr', '.es', '.at', '.com.au']

    ext = re.split("^http://"+"(.*?)"+".ebay"+"(.*?)"+"/"+"(.*?)", url)[2] #extract the extension from the url
    sinstance['domain'] = domain_names[domain_extensions.index(ext)] #match the extension to the name of the domain

    #custom name of this search request
    if name:
        sinstance['name']= name

    return sinstance

