from flask import Flask


app = Flask('__name__', static_folder = 'web_folder/static',   template_folder = 'web_folder/templates')#, instance_relative_config=True)

app.config.update(
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
print "Static folder", app.static_folder
print
# app.config.from_object('config')
# app.config.from_pyfile('config.py') #from instance folder (sensitive config) #TODO - fix the bug
