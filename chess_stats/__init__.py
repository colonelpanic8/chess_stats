from __future__ import absolute_import
import os

from flask import Flask, url_for

# class CustomFlask(Flask):
#     jinja_options = Flask.jinja_options.copy()
#     jinja_options.update(dict(
#         block_start_string='{%',
#         block_end_string='%}',
#         variable_start_string='<%',
#         variable_end_string='%>',
#         comment_start_string='<#',
#         comment_end_string='#>',
#     ))


application_directory = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.jinja_env.globals['get_static_url'] = lambda filename: url_for('static', filename=filename)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'sqlite:///{app_dir}/testing.db'.format(
        app_dir=application_directory
    )
)
app.debug = True

