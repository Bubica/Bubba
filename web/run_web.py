# from celery import Celery
# from flask import Flask, request, session, g, redirect, url_for, \
     # abort, render_template, flash

"""
Run:
>>> redis-server

From  "web" folder:
>>> celery worker -A web_folder.celery_worker.celery --loglevel=info
>>> python -m run_web
"""
import subprocess
from web_folder import app
import web_folder.views 


if __name__ == '__main__':
    print "Starting flask app...."
    app.run()
