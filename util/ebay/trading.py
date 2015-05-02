from ebay.trading import get_response
import requests
from ebay.utils import (get_endpoint_response, get_config_store)
from lxml import etree


# Item Data
def GetItem(item_id, outputSelector=None, detailLevel = None, encoding="JSON"):

    #get the user auth token
    token = get_config_store().get("auth", "token")

    root = etree.Element("GetItemRequest", xmlns="urn:ebay:apis:eBLBaseComponents")

    #add it to the xml doc
    credentials_elem = etree.SubElement(root, "RequesterCredentials")
    token_elem = etree.SubElement(credentials_elem, "eBayAuthToken")
    token_elem.text = token

    itemID_elem = etree.SubElement(root, "ItemID")
    itemID_elem.text = str(item_id)

    if outputSelector:
        outputSelector_elem = etree.SubElement(root, "OutputSelector")
        outputSelector_elem.text = item

    if detailLevel:
        detailLevel_elem = etree.SubElement(root, "DetailLevel")
        detailLevel_elem.text = detailLevel

     #need to specify xml declaration and encoding or else will get error
    request = etree.tostring(root, pretty_print=False,
                             xml_declaration=True, encoding="utf-8")

    response = get_response("GetItem", request, encoding)

    return response #NOTE: it returns an xml reposnse, not a dict
