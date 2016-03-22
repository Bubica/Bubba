from celery import Celery
from celery.signals import worker_shutdown

from flask import Flask
from flask import Response
from flask import render_template, flash, redirect, jsonify, request, make_response, url_for
import json
import time
import random
import copy
from . import web_app # this is a Flask instance
import os
import pagination
from app.ebay import feed_launcher

"""
================================================================================================
This module contains all things celery related.

We start a worker (in the background on the local machine) with:

    celery worker -A web.celery_worker.celery_app --loglevel=info  & 

, where web.celery_worker.celery_app is the name of the Celery application we are 
running in the started worker.
================================================================================================
"""
#Redirect output (with autoflush)
import sys
sys.stdout = open('celery_output.txt', 'w',0)

def make_celery(web_app):
    """
    ================================================================================================
    Creates a Celery application instance, defines a task class (extends a standard TaskBase class)
    and associates it to the created instance (celery.Task). Returns created celery object.

    broker is the service used for sending/receiving messages. Here I used Reddis
    ================================================================================================
    """
    celery = Celery(web_app.import_name, broker = web_app.config['CELERY_BROKER_URL'])
    celery.conf.update(web_app.config)
    
    #Redefinition of task prototype -- not sure why is this cutomization needed
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with web_app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask

    return celery

def _cleanup():
    #Delete temp html files in templates folder
    for f in os.listdir(web_app.template_folder):
        if f[:4] == 'temp':
            os.remove(f)

#Data structures
celery_app = make_celery(web_app) #celery worker for fetching feed

ebayLauncher = feed_launcher.Launcher(web_app.static_folder + '/logs')
paginator = pagination.Paginator(web_app.template_folder)

@celery_app.task(name='web_folder.celery_worker.feed_load_bckg', bind=True)
def feed_load_bckg(self): 

    """
    #########################
    EBAY FETCH TASK:

    This method creates a task inside celery app instance.
    #########################
    """

    #Init Structures
    # global ebayLauncher
    # global paginator

    done = False
    i=0

    gen = ebayLauncher.searchGenerator()
    while not done:
        i+=1
        time.sleep(3)
        message = 'Nothing'
        self.update_state(state='PROGRESS', meta={'pgCnt': paginator.getPgCount(), 'searchCnt':i, 'status': message}) 

        try:
            res = gen.next()
            paginator.addItems(res)

        except StopIteration:
            #terminate when all searches have been run
            done = True

    return {'pgCnt': paginator.getPgCount(), 'searchCnt':i, 'status': 'FINISHED!', 'done':'yes'}
