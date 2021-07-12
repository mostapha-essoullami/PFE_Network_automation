from flask import Flask, request
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename


app = Flask(__name__)
basedir=os.path.join(os.path.dirname(app.instance_path),"myproject")
tftp_path=folder_path=os.path.join(basedir, 'tftp')

app.config['SECRET_KEY'] = 'testtt'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False

db=SQLAlchemy(app)
Migrate(app,db)


from myproject.command.view import command_blueprint
from myproject.devices.view import devices_blueprint
from myproject.files.view import files_blueprint
from myproject.projects.view import projects_blueprint
from myproject.ansible.view import ansible_blueprint

app.register_blueprint(command_blueprint,url_prefix="/command")
app.register_blueprint(devices_blueprint,url_prefix="/devices")
app.register_blueprint(files_blueprint,url_prefix="/files")
app.register_blueprint(projects_blueprint,url_prefix="/projects")
app.register_blueprint(ansible_blueprint,url_prefix="/ansible")
