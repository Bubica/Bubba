def test1():

    """ Testing feed module on provisional urls """

    import feed
    from url import ebayUrl
    import setup

    setup.init()


    """
    Testing ebayUrl and feed modules.
    """


    urls = [
    'http://www.ebay.co.uk/sch/Womens-Handbags-/169291/i.html?_from=R40&_nkw=whistles&_sop=10',
    'http://www.ebay.co.uk/sch/Jewellery-Watches-/281/i.html?_msacat=50637%7C155101&_sac=1&_sop=10&_nkw=all+saints+-vampire+-jesus+-stretch&LH_PrefLoc=1',
    'http://www.ebay.co.uk/sch/m.html?_odkw=&_sop=10&_ssn=1saigon1&hash=item3aa1b7bcf6&item=251821276406&pt=UK_Women_s_Dresses&_osacat=0&_from=R40&_trksid=p2046732.m570.l1313.TR0.TRC0.H0.Xdress.TRS0&_nkw=dress&_sacat=0',
    'http://www.ebay.co.uk/sch/m.html?item=251821276406&hash=item3aa1b7bcf6&pt=UK_Women_s_Dresses&_ssn=1saigon1&_sop=10&rt=nc',
    'http://www.ebay.co.uk/sch/Womens-Accessories-/4251/i.html?_msacat=3009%7C53159%7C63861%7C63862%7C63863%7C63864%7C63866%7C169001&_from=R40&_nkw=reiss+-6+-8+-16&_sop=10'
    ]

    eFeed = feed.UserFeed(userID="0", log_folder='./', fetchTDelay = 60)

    for url in urls:
        si = ebayUrl.parse(url)
        r2 = eFeed.loadSearch(si)

    for url in eFeed.searches:
        si = ebayUrl.parse(url)
        res = eFeed.searches[url]
        print si['keywords'], "----", len(res)


def test2():
    import feed_launcher
    import feed
    
    """Testing feed_launcher on bookmarks """
    l = feed_launcher.Launcher()
    res = l.runNext()

