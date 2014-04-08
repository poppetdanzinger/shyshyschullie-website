from flask import render_template, url_for, flash, redirect, g, session, request
from app import app

#from app.scripts.events import *
from app.scripts.shyshycalendar import EventManager
import traceback,sys

@app.route('/')
def home():
    error_msgs=[]
    try:
        events=EventManager(verbose=app.debug).events
    except Exception as e:
        if app.debug:
            print(e)
        events=[]
        exc_type,exc_value,exc_traceback=sys.exc_info()
        error_msgs=traceback.format_exception(exc_type, exc_value,exc_traceback)

    return render_template('home.html',
                           title = "Shy Shy Homepage",
                           events=events,
                           error_msgs=error_msgs)

@app.route('/blog/<blog_id>')
def blog(blog_id):
    print(blog_id)
    return render_template('blog.html',
                           title="Shy Shy Blog")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    error_msgs=traceback.format_exception(type(e), str(e),e.__traceback__)
    return render_template('500.html',error_msgs=(str(e)),), 500
