from flask import render_template, url_for, flash, redirect, g, session, request
from app import app

from app.scripts.events import *

@app.route('/')
def home():
    events=get_events()
    return render_template('home.html',
                           title = "Shy Shy Homepage",
                           events=events)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
