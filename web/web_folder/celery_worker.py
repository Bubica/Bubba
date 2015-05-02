from celery import Celery
from flask import Flask
from flask import Response
from flask import render_template, flash, redirect, jsonify, request, make_response, url_for
import json
import time
import random
import copy
from . import app
import os
import pagination
# import pagination2

import sys
sys.path.append('/Users/bubica/Development/CODE/HOBBY_PROJECTS/ebaySearchFeed/') #TODO handle this
import feed_launcher

def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

def _cleanup():
    #Delete temp html files in templates folder
    for f in os.listdir(app.template_folder):
        print f
        if f[:4] == 'temp':
            os.remove(f)

#Data structures
celery = make_celery(app)
ebayLauncher = None
paginator = None

#Delete previous fetch results
# _cleanup()

@celery.task(name='web_folder.celery_worker.feed_load_bckg', bind=True)
def feed_load_bckg(self): #for some reason I can NOT pass additional arguments besides self

    # LONG RUNNING TASK EXEC

    #Init Structures
    global ebayLauncher
    global paginator
    ebayLauncher = feed_launcher.Launcher(app.static_folder + '/logs')
    paginator = pagination.Paginator(app.template_folder)

    print "Running..."
    done = False
    i=0
    while not done:
        i+=1
        time.sleep(3)
        message = 'Nothing'
        self.update_state(state='PROGRESS', meta={'pgCnt': paginator.getPgCount(), 'searchCnt':i, 'status': message}) 
        # self.update_state(state='PROGRESS', meta={'pgCnt': 1, 'searchCnt':i, 'status': message}) 

        print
        print "CELERY:      running next search"
        res = ebayLauncher.runNext()
        paginator.addItems(res)

        #terminate when all searches have been run
        if res is None: done = True

    print "Celery ---- DONE! All searches finished!" 
    return {'pgCnt': paginator.getPgCount(), 'searchCnt':i, 'status': 'FINISHED!', 'done':'yes'}
