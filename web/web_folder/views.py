from flask import render_template, flash, redirect, jsonify, request, make_response, url_for, Response
import json
import os

from . import app
import celery_worker #TODO - it performs initialization of the celery! Work around that


@app.route('/', methods=['GET', 'POST'])
@app.route('/index',  methods=['GET', 'POST'])
def show_feed():

    """ Renders feed html page but loading of items happens in the background task """

    print "Starting feed"

    entries = []
    return render_template('show_feed.html' , entries=entries)

@app.route('/feed/<int:pgNo>', methods=['GET'])
@app.route('/feed/<int:pgNo>.html', methods=['GET'])
def get_feed_pg(pgNo):

    """ Used for infinite scroll """
    
    print ("Rendering page "+str(pgNo));
    tmpl = "temp"+str(pgNo)+'.html'
    dir_tmpl_list = os.listdir(app.template_folder)
    
    if tmpl in dir_tmpl_list:
        return render_template(tmpl)

    return 'None' #Has to return string

@app.route('/login', methods=['GET', 'POST'])
def login():
    print "Login method"
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

    print "LOADING FEED"
    celery_task =  celery_worker.feed_load_bckg.apply_async()
    print "Background feed load started, ID:", str(celery_task.id)
    return jsonify({}), 202, {'Location': url_for('feed_update', task_id=celery_task.id)}


@app.route('/feed_update/<task_id>')
def feed_update(task_id):
    
    task =  celery_worker.feed_load_bckg.AsyncResult(task_id)
    print "Task id", task_id

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

@app.route('/exit')
def dump_logs():
    """ Dump all logs """
    celery_worker.ebayLauncher.log_feed_launch() 
    return 'OK' #must return some value...

@app.route('/log_ignore_seller', methods=['GET'])
def log_ignored_seller():
    sellerID = request.args.get('sellerId', type=str)
    celery_worker.ebayLauncher.log_ignored_seller(sellerID)
    return 'OK'

@app.route('/log_ignore_item', methods=['GET'])
def log_ignored_item():
    item_id = request.args.get('item_id', type=str)
    search_id = request.args.get('search_id', type=str)

    celery_worker.ebayLauncher.log_ignored_item(search_id, item_id)
    return 'OK'
