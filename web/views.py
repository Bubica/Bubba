from flask import render_template, flash, redirect, jsonify, request, make_response, url_for, Response
import json
import os
import shutil
import datetime
from app.ebay import feed_launcher
from . import web_app as app
import celery_worker #TODO - it performs initialization of the celery! Work around that

#Redirect output (with autoflush)
import sys
sys.stdout = open('views_output.txt', 'w',0)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index',  methods=['GET', 'POST'])
def show_feed():

    """ Renders feed html page but loading of items happens in the background task """
    entries = []
    return render_template('show_feed.html' , entries=entries)

@app.route('/feed/<int:pgNo>', methods=['GET'])
@app.route('/feed/<int:pgNo>.html', methods=['GET'])
def get_feed_pg(pgNo):

    """ Used for infinite scroll """
    tmpl = "temp"+str(pgNo)+'.html'
    dir_tmpl_list = os.listdir(app.template_folder)
    
    if tmpl in dir_tmpl_list:
        return render_template(tmpl)

    return 'None' #Has to return string

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


""" CELERY INTERFACE """

""" Celery - background feed load """
@app.route('/feed_load', methods = ['POST'])
def feed_load():
    celery_task =  celery_worker.feed_load_bckg.apply_async()
    return jsonify({}), 202, { \
    'update_url': url_for('feed_update', task_id=celery_task.id), \
    'terminate_url': url_for('feed_terminate', task_id=celery_task.id), \
    'log_url': url_for('log')}

@app.route('/feed_update/<task_id>')
def feed_update(task_id):
    
    """ Updates the state of the background task """

    task =  celery_worker.feed_load_bckg.AsyncResult(task_id)
    if task.state == 'PENDING':
        # job did not start yet
        resp = {
            'state': task.state,
            'pgCnt': 0,
            'searchCnt': 0,
            'status': 'Pending...'
            
        }
    elif task.state != 'FAILURE':
        resp = {
            'state': task.state,
            'pgCnt': task.info.get('pgCnt', 0),
            'searchCnt': task.info.get('searchCnt', 1),
            'status': task.info.get('status', ''),
        }

        if 'done' in task.info:
            resp['done'] = task.info['done']
    else:
        # something went wrong in the background job
        resp = {
            'state': task.state,
            'pgCnt': -1,
            'searchCnt': -1,
            'status': str(task.info)  # this is the exception raised
            
        }

    return Response(json.dumps(resp),  mimetype='application/json')

@app.route('/feed_terminate/<task_id>')
def feed_terminate(task_id):
    #stop the feed generating task
    task =  celery_worker.feed_load_bckg.AsyncResult(task_id)
    task.revoke(terminate = True)

    #copy temp_dump page into the last items page (to be displayed)
    temp_fname = app.template_folder + "/temp_dump.html"
    if (os.path.isfile(temp_fname)):

        #Find the last items page
        pg_cnt = 2
        while os.path.isfile(app.template_folder +'/temp'+str(pg_cnt)+".html"): pg_cnt +=1

        shutil.copyfile(temp_fname, app.template_folder + "/temp"+str(pg_cnt)+".html")
        os.remove(temp_fname) 

    return 'OK' #must return some value...

""" Logging happens after the feed fetch celery task has finished """

@app.route('/log', methods=['POST'])
def log():
    #Extract ignored items form the request
    items = request.form['items']
    
    if len(items) > 0:
        items = items.split(',') #list of items id and search ids
        items = [{'search_id': items[i+1], 'item_id': items[i], 'end_t': None} for i in range(0, len(items), 3 )] #create (searchid, itemid) tuples
    else:
        items = []
        
    #Extract ignored sellers
    sellers = request.form['sellers']

    if len(sellers) >0:
        sellers = sellers.split(',') #list of seller ids
    else:
        sellers = []

    #Extract the id of the last search that has been displayed
    last_search = request.form['last_search']

    #Obtain access to "db" that is currently only a set of files
    feed_manip = feed_launcher.Launcher(app.static_folder + '/logs')
    r = feed_manip.exit(sellers, items, [])

    return 'OK'

