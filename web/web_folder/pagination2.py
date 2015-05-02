"""
Instance of this class are used to generate html files that will be added to the feed in infinite scroll script.


This does not work! Because get_feed_pg DOES NOT SEE changes made by celery process to item_buffer!
"""

from flask import render_template_string
from . import app

ITEMS_PER_PAGE = 50
item_buffer = []

def addItems(items):
    item_buffer.append(items)

@app.route('/feed/<int:pgNo>', methods=['GET'])
def get_feed_pg(pgNo):

    assert pgNo>=1
 
    pg_items = item_buffer [ITEMS_PER_PAGE * (pgNo-1) : ITEMS_PER_PAGE * pgNo]

    print 
    print "PAGINATION: "
    print "PAGE SIZE", len(pg_items)
    print "BUFF SIZE", len(item_buffer)
    print 

    return render_template_string(feed_template, entries=pg_items)

feed_template = """

<head>
    {% block head %}
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js"></script>
    <script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
    <script src="http://api.atmosonline.com/rest/namespace/infinitescroll/jquery.infinitescroll.min.js?uid=da8dd05dea2a4ee78ecd636db084bf47%2FA059402892dfadf9552c&expires=1403203192&signature=UciaR6fu6KdQd4ug9X608FXhqSA%3D"></script>

    {% endblock %}
</head>

{% block content %}
  <div id="container"">
    {% for entry in entries %}
    <div class="item">
      <span class="Centerer nonselect">
            <h2> {{entry.searchName}} </h2>
            <img src="{{ entry.pictureURL }}"/> 
            <a href="{{ entry.itemURL}}" class="button hvr-grow hidden" target="_blank">View</a>
            <a href="#" class="button hvr-grow hidden" id = "ignore_seller" name="{{ entry.sellerId }}">Ignore this seller</a>
      </span>
    </div>
    {% endfor %}
  </div>

{% endblock %}
"""