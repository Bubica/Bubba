#!/usr/bin/python
#
# Parse the ebay bookmarks folders in local Safari bookmarks and return tree representations of such folders.
# Each bookmark folder is represented with search.SearchGroup object and each link is represented with search.SearchRequest object

import sys, os, codecs, plistlib

from .. import search
from .parser import parse

book_fname = "Library/Safari/Bookmarks.plist"

def load(folderPrefix = 'ebay searches'):

    xmlBook = _read_bookmarks()

    rootGroup = search.SearchGroup('root')

    count = _filter(xmlBook,  rootGroup, folderPrefix = folderPrefix)
    
    return rootGroup, count


def _read_bookmarks():
    global  book_fname
    bookmarks_file = os.path.join(
        os.getenv("HOME"),
        book_fname
    )
    return _parsePlist(bookmarks_file)

def _parsePlist(bookmarks_file):
    try:
        return plistlib.Plist.fromFile(bookmarks_file)
    except:
        os.system("/usr/bin/plutil -convert xml1 %s" % bookmarks_file )
        xmlContent = plistlib.Plist.fromFile(bookmarks_file)
        os.system("/usr/bin/plutil -convert binary1 %s" % bookmarks_file )
        return xmlContent

def _filter(xmlTag, rootNode, ebayFlag = 0, depth = 0, folderPrefix="", _searchCnt =0):
    
    """
    Only retaining the bookmarks in "ebay searches" folder.
    The retained ones are converted into search objects.
    """
    xmlTag_type  = xmlTag.get("WebBookmarkType")
    xmlTag_title = xmlTag.get("Title")

    if xmlTag_type == "WebBookmarkTypeList":

        #FOLDER

        if folderPrefix in xmlTag_title.lower():
            ebayFlag = 1 #this folder and all its descendants containe ebay related searches

        if ebayFlag:

            newRootNode = search.SearchGroup(xmlTag_title)
            newRootNode.setParent(rootNode)
            rootNode.addChild(newRootNode)

            rootNode = newRootNode

        for tag in xmlTag.get("Children", []):
            _searchCnt = _filter(tag, rootNode, ebayFlag, (depth+1), folderPrefix, _searchCnt) 


    elif xmlTag_type == "WebBookmarkTypeLeaf":

        #LINK

        if ebayFlag:  

            #parse url content
            url = xmlTag["URLString"]
            name = xmlTag["URIDictionary"]['title'] #bookmark name - as defined by the user
            
            s = parse(url, name)

            if s:
                s.setSearchGroup(rootNode)
                rootNode.addChild(s)

                _searchCnt +=1

    return _searchCnt

