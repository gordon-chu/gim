from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail

# Define the WSGI application object
app = Flask(__name__)

# Configurations
app.config.from_object('config.ProductionConfig')

# set maximum upload file size to 100 MB
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

# Define mail
mail = Mail(app)

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)

# Define the Bcrypt cryptographic object
flask_bcrypt = Bcrypt(app)

# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return '404', 404

# Import a module / component using its blueprint handler variable (mod_auth)
from app.mod_api.api import mod_api as api_module

# Register blueprint(s)
app.register_blueprint(api_module)

# Build the database:
# This will create the database file using SQLAlchemy
db.create_all()

# Initialize permissions and Usergroups
from app.mod_api import models
models.Permission.initialize_permissions()
models.Usergroup.initialize_usergroups()

