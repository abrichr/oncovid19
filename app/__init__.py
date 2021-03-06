import logging
import os
from pprint import pformat

from flask import Flask, flash, redirect, request, url_for
from flask_misaka import Misaka
from flask_sslify import SSLify
from flask_toastr import Toastr
from slugify import slugify


app = Flask(__name__)

# Setup the app with the config.py file
app.config.from_object('app.config')

# Setup the logger
from app.logger_setup import logger

logger.warning('*' * 40)
DEBUG = os.environ.get('DEBUG', 0)
logger.warning('DEBUG: {}'.format(DEBUG))
is_debug = bool(int(DEBUG))
logger.warning('is_debug: {}'.format(is_debug))
app.debug = is_debug
logger.warning('*' * 40)

toastr = Toastr(app)
Misaka(app, autolink=True)

sslify = SSLify(app)

# Setup the database
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

# Setup the mail server
from flask_mail import Mail
mail = Mail(app)

# Setup the debug toolbar
from flask_debugtoolbar import DebugToolbarExtension
app.config['DEBUG_TB_TEMPLATE_EDITOR_ENABLED'] = True
app.config['DEBUG_TB_PROFILER_ENABLED'] = True
toolbar = DebugToolbarExtension(app)

# Setup the password crypting
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

# Import the views
from app.views import main, user, project, error, comment
app.register_blueprint(user.userbp)
app.register_blueprint(project.projectbp)
app.register_blueprint(comment.commentbp)

# Setup the user login process
from flask_login import LoginManager
from app.models import User

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'userbp.signin'


@login_manager.user_loader
def load_user(email):
    user = User.query.filter(User.email == email).first()
    print('load_user() email:', email, 'user:', pformat(vars(user)) if user else '')
    return user


@login_manager.unauthorized_handler
def handle_needs_login():
    flash(
        'You have to be logged in to access the page at {}'.format(
            request.path
        )
    )
    return redirect(url_for('userbp.signin', next=request.path))


@app.context_processor
def inject_is_active_route():
    is_active_route = True
    return dict(is_active_route=is_active_route)


'''
@app.context_processor
def dump_request():
    from pprint import pprint
    print('request:')
    pprint(vars(request))
'''


@app.context_processor
def inject_is_active_route():
    def is_active_route(endpoint):
        return (
            request.url_rule.endpoint == endpoint
            if request.url_rule else None
        )
    return dict(is_active_route=is_active_route)


@app.context_processor
def inject_slugify():
    return dict(slugify=slugify)


from app import admin
