from flask import Blueprint, Flask, render_template, redirect, url_for, request
from myproject.ansible.form import EditForm, CreateForm
from myproject.projects.view import folderpath, subprojectselected
import os
from werkzeug.utils import secure_filename


ansible_blueprint= Blueprint('ansible',__name__,template_folder="templates")

@ansible_blueprint.route('/ansible')
def listplays():
    folderdir=folderpath()
    if folderdir:
        path= os.path.join(folderdir, 'ansible')
        files=os.listdir(path)
        files.remove("hosts")
        files.remove("host_vars")
        print(files)
        return render_template('playbooks.html',playbook=files)
    else:
        return redirect(url_for("projects.viewid"))

@ansible_blueprint.route('/run/<file>')
def run(file):
    if subprojectselected():
        cmd="ansible-playbook {} ".format(os.path.join(folderpath(), 'ansible',file))
        f=open("ansible.cfg","w+")
        f.write("[defaults] \ninventory = "+os.path.join(folderpath(), 'ansible','hosts')+"\nhost_key_checking = False")
        f.close()
        print(cmd)
        
        result=os.popen(cmd).read()
        print("+++++++++++")
        print(result)
        return render_template('playresult.html',results=result,file=file)
    else:
        return redirect(url_for("projects.viewid"))    
@ansible_blueprint.route('/deleteplay/<file>')
def deleteplay(file):
    if subprojectselected():
        path= os.path.join(folderpath(), 'ansible',file)

        print("removing "+str(file))
        os.remove(path)

    return redirect(url_for('ansible.listplays'))


@ansible_blueprint.route('/play/<file>', methods=['GET', 'POST'])
def playedit(file):
    if subprojectselected():
        form = EditForm()
        print(file)
        print(form.validate_on_submit())
        path= os.path.join(folderpath(), 'ansible',file)
        f=open(path,'r')
        aa=f.read()
        f.close()
        print(aa)
        print("editng "+str(file))
        if form.validate_on_submit():
            print("********")
            f=open(path,'w')
            print(repr(form.ansibleplay.data))
            f.writelines(form.ansibleplay.data.split("\r"))
            f.close()
            return redirect(url_for('ansible.listplays'))
        form.ansibleplay.data=aa
        
        return render_template('editplay.html',form=form,file=file)
    else:
        return redirect(url_for("projects.viewid"))

@ansible_blueprint.route('/addplay', methods=['GET', 'POST'])
def addplay():
    if subprojectselected():
        form = CreateForm()

        if form.validate_on_submit():

            playbook = form.ansibleplay.data
            filename = secure_filename(form.playname.data)
            print(filename)
            f=open( os.path.join(folderpath(), 'ansible',filename),"w+")
            f.writelines(playbook.split("\r"))
            f.close()
    
            return redirect(url_for('ansible.listplays'))
        return render_template('addplay.html',form=form)
    else:
        return redirect(url_for("projects.viewid"))
    






@ansible_blueprint.route('/hostvars')
def hosts_vars():
    folderdir=folderpath()
    if folderdir:
        path= os.path.join(folderdir, 'ansible','host_vars')
        files=os.listdir(path)
        
        print(files)
        return render_template('hostvars.html',host_vars=files)
    else:
        return redirect(url_for("projects.viewid"))

    
@ansible_blueprint.route('/deletehostvar/<file>')
def deletehostvar(file):
    if subprojectselected():
        path= os.path.join(folderpath(), 'ansible','host_vars',file)

        print("removing "+str(file))
        os.remove(path)

    return redirect(url_for('ansible.hosts_vars'))


@ansible_blueprint.route('/host/<file>', methods=['GET', 'POST'])
def hostvaredit(file):
    if subprojectselected():
        form = EditForm()
        print(file)
        print(form.validate_on_submit())
        path= os.path.join(folderpath(), 'ansible','host_vars',file)
        f=open(path,'r')
        aa=f.read()
        f.close()
        print(aa)
        print("editng "+str(file))
        if form.validate_on_submit():
            print("********")
            f=open(path,'w')
            print(repr(form.ansibleplay.data))
            f.writelines(form.ansibleplay.data.split("\r"))
            f.close()
            return redirect(url_for('ansible.hosts_vars'))
        form.ansibleplay.data=aa
        
        return render_template('edithostvar.html',form=form,file=file)
    else:
        return redirect(url_for("projects.viewid"))

@ansible_blueprint.route('/addhost', methods=['GET', 'POST'])
def addhostvar():
    if subprojectselected():
        form = CreateForm()

        if form.validate_on_submit():

            playbook = form.ansibleplay.data
            filename = secure_filename(form.playname.data)
            print(filename)
            f=open( os.path.join(folderpath(), 'ansible','host_vars',filename),"w+")
            f.writelines(playbook.split("\r"))
            f.close()
    
            return redirect(url_for('ansible.hosts_vars'))
        return render_template('addhostvar.html',form=form)
    else:
        return redirect(url_for("projects.viewid"))