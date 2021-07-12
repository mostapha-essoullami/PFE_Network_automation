from flask import Blueprint, Flask, render_template, redirect, url_for,  make_response,request
import os
import shutil
import pandas as pd
from myproject.models import Project, Folder, Devices
from myproject.projects.form import NewProjectForm, NewFolderForm
from myproject import db, basedir
from werkzeug.utils import secure_filename
import paramiko
from datetime import datetime

def subprojectselected():
    if request.cookies.get('folder_id'):
        return True
    else:
        return False
        
def folderpath():
    if subprojectselected():
        project_id=int(request.cookies.get('project_id'))
        folder_id=int(request.cookies.get('folder_id'))

        folder_path=os.path.join(basedir, 'directory',secure_filename(Project.query.get(project_id).name),secure_filename(Folder.query.get(folder_id).name))
        return folder_path
    else:
        return None

projects_blueprint= Blueprint('projects',__name__,template_folder="templates")

@projects_blueprint.route('/project', methods=['GET', 'POST'])
def listprojects():
    projects=Project.query.all()
    print(projects)
    return render_template('project.html',projects=projects)

@projects_blueprint.route('/createproject', methods=['GET', 'POST'])
def createproject():
    form = NewProjectForm()
    print(form.validate_on_submit())
    if form.validate_on_submit():
        name=form.name.data
        description=form.description.data
 
        os.mkdir(os.path.join(basedir, 'directory',secure_filename(name)))
        proj=Project(name,description)
        db.session.add(proj)
        all=Project.query.all()
        print(all)
        db.session.commit()
        return redirect(url_for('projects.listprojects'))

    return render_template('createproject.html',form=form)


@projects_blueprint.route('/viewproject/<id>')
def viewproject(id):
    resp = make_response(redirect(url_for("projects.viewid")))
    resp.set_cookie('project_id', id)
    print(id)
    return resp


@projects_blueprint.route('/delete')
def delete():
    if request.cookies.get('project_id'):
        id=int(request.cookies.get('project_id'))
        project=Project.query.get(id)
        db.session.delete(project)
        db.session.commit()
        shutil.rmtree(os.path.join(basedir, 'directory',secure_filename(project.name)))
        resp = make_response(redirect(url_for('projects.listprojects')))
         # Delete cookie
        resp.delete_cookie("project_id")
        resp.delete_cookie("folder_id")

        return resp
    else:
        return redirect(url_for('projects.listprojects'))


@projects_blueprint.route('/deletefolder')
def deletefolder():
    if subprojectselected():
        folder_id=int(request.cookies.get('folder_id'))
        project_id=int(request.cookies.get('project_id'))
        project=Project.query.get(project_id)
        folder=Folder.query.get(folder_id)
        db.session.delete(folder)
        db.session.commit()
        shutil.rmtree(os.path.join(basedir, 'directory',secure_filename(project.name),secure_filename(folder.name)))
        resp = make_response(redirect(url_for('projects.viewid')))
         # Delete cookie
        resp.delete_cookie("folder_id")
        return resp
    else:
        return redirect(url_for('projects.viewid'))

@projects_blueprint.route('/view')
def viewid():
    if request.cookies.get('project_id'):
        id=int(request.cookies.get('project_id'))
        project=Project.query.get(id)
        print(id)
        files=project.folders

        print(files)
        return render_template('files.html',folders=files,id=id,name=project.name, description=project.description)
    else:
        return redirect(url_for('projects.listprojects'))

@projects_blueprint.route('/createfolder', methods=['GET', 'POST'])
def createfolder():
    form = NewFolderForm()
    project_id=int(request.cookies.get('project_id'))
    if form.validate_on_submit():
        name=form.name.data
        description=form.description.data
        
        folderdir=os.path.join(basedir, 'directory',secure_filename(Project.query.get(project_id).name),secure_filename(name))
        os.mkdir(folderdir)
        os.mkdir(os.path.join(folderdir,"csv"))
        os.mkdir(os.path.join(folderdir,"jinja"))
        os.mkdir(os.path.join(folderdir,"config-files"))
        os.mkdir(os.path.join(folderdir,"ansible"))
        os.mkdir(os.path.join(folderdir,"ansible","host_vars"))
        f=open(os.path.join(folderdir,"ansible","hosts"),"x")
        f.close()
        
        folder=Folder(name,description,project_id)
        db.session.add(folder)
        all=Folder.query.all()
        print(all)
        db.session.commit()
        return redirect(url_for('projects.viewproject',id=project_id))

    return render_template('createfolder.html',form=form)

@projects_blueprint.route('/viewfolder/<id>')
def viewfolder(id):
    resp = make_response(redirect(url_for("projects.dashboard")))
    resp.set_cookie('folder_id', id)
    return resp

@projects_blueprint.route('/dashboard')
def dashboard():
    if subprojectselected():
        project_id=int(request.cookies.get('project_id'))
        folder_id=int(request.cookies.get('folder_id'))
        folder=Folder.query.get(folder_id)
        all=Devices.query.filter_by(folder_id=folder_id)
        total=0
        noping=0
        nossh=0
        for dev in all:
            total+=1
            if dev.pingable=="No":
                noping+=1
                nossh+=1
            elif dev.sshable=="No":
                nossh+=1
        return render_template('dashboard.html',devices=all, name=folder.name, description=folder.description,total=total,noping=noping,nossh=nossh)
    
    else:
        return redirect(url_for("projects.viewid"))



@projects_blueprint.route('/devcheck/<id>')
def check(id):
    dev=Devices.query.get(id)
    response = os.system("ping -c 2 " + dev.ip)
    message=""
    error=False
    if response == 0:
        dev.pingable="Yes"
    else:
        dev.pingable="No"
        dev.sshable="No"
        dev.message="verifie IP address"
        error=True
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if not(error):
            ssh.connect(dev.ip, username=dev.username, password=dev.password)
            dev.sshable="Yes"
            dev.message="Last Check in"+datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    except paramiko.AuthenticationException:
        dev.sshable="No"
        dev.message="Authentication failed, please verify your credentials:"
    except paramiko.SSHException as sshException:
        dev.sshable="No"
        dev.message="Unable to establish SSH connection: %s" % sshException
    except paramiko.BadHostKeyException as badHostKeyException:
        dev.sshable="No"
        dev.message="Unable to verify server's host key: %s" % badHostKeyException
    except Exception as unknown_error:
        dev.sshable="No"
        dev.message='Some other error: ' + str(unknown_error)
    finally:
        db.session.add(dev)
        db.session.commit()
        ssh.close()
        return redirect(url_for("projects.dashboard"))



@projects_blueprint.route('/csv/<file>')
def csvread(file):
    project_id=int(request.cookies.get('project_id'))
    folder_id=int(request.cookies.get('folder_id'))

    folder_path=os.path.join(basedir, 'directory',secure_filename(Project.query.get(project_id).name),secure_filename(Folder.query.get(folder_id).name))
    path= os.path.join(folder_path, 'csv',file)
    ps=pd.read_csv(path,sep=";")
    print("****************************")
    return ps.to_html(index=False)


