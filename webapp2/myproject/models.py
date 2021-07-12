from datetime import datetime
from myproject import db


class Project(db.Model):
    __tablename__ = 'project'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.Text)
    description=db.Column(db.Text)
    date=db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
   
    folders=db.relationship('Folder',backref='project',lazy='dynamic', cascade="all, delete-orphan")

    def __init__(self,name,description):
        self.name=name
        self.description=description

    def __repr__(self):
        return f"project {self.name} detail: {self.description} created at {self.date} "

class Folder(db.Model):
    __tablename__ = 'folder'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.Text)
    description=db.Column(db.Text)
    date=db.Column(db.DateTime,nullable=False,default=datetime.utcnow)

    project_id=db.Column(db.Integer,db.ForeignKey('project.id'))
    devies=db.relationship('Devices',backref='Folder',lazy='dynamic', cascade="all, delete-orphan")
    logs=db.relationship('Logs',backref='Folder',lazy='dynamic', cascade="all, delete-orphan")
    def __init__(self,name,description,project_id):
        self.name=name
        self.description=description
        self.project_id=project_id
    def __repr__(self):
        return f"folder {self.name} detail: {self.description} created at {self.date} "


class Devices(db.Model):

    id=db.Column(db.Integer,primary_key=True)
    hostname=db.Column(db.Text)
    ip=db.Column(db.Text)
    username=db.Column(db.Text)
    password=db.Column(db.Text)
    devicetype=db.Column(db.Text)
    folder_id=db.Column(db.Integer,db.ForeignKey('folder.id', ondelete='CASCADE'))
    pingable=db.Column(db.Text,default="no")
    sshable=db.Column(db.Text,default="no")
    message=db.Column(db.Text,default="not checked")

    def __init__(self,hostname,ip,username,password,devicetype,folder_id):
        self.hostname=hostname
        self.ip=ip
        self.username=username
        self.password=password
        self.devicetype=devicetype
        self.folder_id=folder_id
    def __repr__(self):
        return f"ip {self.ip} hostname {self.hostname} type {self.devicetype}"

class Logs(db.Model):

    id=db.Column(db.Integer,primary_key=True)
    hostname_ip=db.Column(db.Text)
    devicetype=db.Column(db.Text)
    folder_id=db.Column(db.Integer,db.ForeignKey('folder.id', ondelete='CASCADE'))
    status=db.Column(db.Text)
    mode=db.Column(db.Text)
    message=db.Column(db.Text)
    command=db.Column(db.Text)
    time=db.Column(db.DateTime,nullable=False,default=datetime.utcnow)

    def __init__(self,hostname,ip,devicetype,folder_id,status,mode,message,command):
        self.hostname_ip=hostname+" |"+ip
        self.devicetype=devicetype
        self.folder_id=folder_id
        self.status=status
        self.mode=mode
        self.message=message
        self.command=command
    def __repr__(self):
        return f"log message {self.message} hostname {self.hostname_ip} type {self.devicetype} command {self.command}"

db.create_all()