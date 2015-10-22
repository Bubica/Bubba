from flask import Flask


web_app = Flask('__name__', static_folder = 'web/static',   template_folder = 'web/templates')#, instance_relative_config=True)

web_app.config.update(
    DATABASE = None,
    DEBUG = True,

    SECRET_KEY = 'development key',
    USERNAME = 'admin',
    PASSWORD = 'buba',
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)
print 
print "Creating app:", __name__
print "Static folder", web_app.static_folder
print
# app.config.from_object('config')
# app.config.from_pyfile('config.py') #from instance folder (sensitive config) #TODO - fix the bug
