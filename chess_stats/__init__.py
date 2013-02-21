import os

from flask import Flask, url_for


application_directory = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.jinja_env.globals['get_static_url'] = lambda filename: url_for('static', filename=filename)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{app_dir}/testing.db'.format(
	app_dir=application_directory
)
#app.debug = True
