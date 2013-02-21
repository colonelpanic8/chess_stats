import os

from flask import Flask, url_for


app = Flask(__name__)
app.jinja_env.globals['get_static_url'] = lambda filename: url_for('static', filename=filename)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
#app.debug = True
