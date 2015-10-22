# from celery import Celery
# from flask import Flask, request, session, g, redirect, url_for, \
     # abort, render_template, flash

"""
Run:
>>> redis-server

From fashionFeed folder:
>>> celery worker -A web.celery_worker.celery --loglevel=info
>>> python -m run_web
"""
import subprocess
from web import web_app
import web.views 


if __name__ == '__main__':
    print "Starting flask app...."
    web_app.run()
