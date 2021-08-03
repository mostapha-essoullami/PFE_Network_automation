from flask import Blueprint, Flask, render_template, redirect, url_for, request
from myproject.devices.form import NewDeviceForm
from myproject.models import Devices
from myproject import db
from myproject.projects.view import folderpath,subprojectselected
import os


devices_blueprint= Blueprint('devices',__name__,template_folder="templates")

@devices_blueprint.route('/add', methods=['GET', 'POST'])
def add():
    if subprojectselected():
        form = NewDeviceForm()
        print(form.validate_on_submit())
        if form.validate_on_submit():
            hostname=form.hostname.data
            password=form.password.data
            username=form.username.data
            devicetype=form.devicetype.data
            ip=form.ip.data
            subproject_id=int(request.cookies.get('subproject_id'))
            
            dev=Devices(hostname,ip,username,password,devicetype,subproject_id)
            db.session.add(dev)
            db.session.commit()
            
            f=open(os.path.join(folderpath(),"ansible","hosts"),"r+")
            originalContent = f.read()
            f.seek(0, 0)
            f.write(dev.devicetype+str(dev.id)+"\n")
            f.write(originalContent)
            f.close()

            f=open(os.path.join(folderpath(),"ansible","host_vars",dev.devicetype+str(dev.id)+".yml"),"w+")
            
            f.write("ansible_host: "+dev.ip+"\nansible_connection: network_cli \nansible_network_os: ios \nansible_become: yes \nansible_become_method: enable \nansible_user: "+dev.username+" \nansible_ssh_pass: "+dev.password)
            f.close()
            return redirect(url_for('devices.listdevices'))

        return render_template('register.html',form=form)
    else:
        return redirect(url_for("projects.viewid")) 
@devices_blueprint.route('/devices')
def listdevices():
    if subprojectselected():
        
        subprojectid=int(request.cookies.get('subproject_id'))
        

        all=Devices.query.filter_by(subproject_id=subprojectid)
        return render_template('List_Devices.html',devices=all)
    else:
        return redirect(url_for("projects.viewid")) 
@devices_blueprint.route('/delete/<id>')
def delete(id):
    if subprojectselected():
        print(id)
        devi=Devices.query.get(id)
        print("removing "+str(devi.id))
        db.session.delete(devi)
        db.session.commit()
        return redirect(url_for('devices.listdevices'))
    else:
        return redirect(url_for("projects.viewid")) 
@devices_blueprint.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    if subprojectselected():
        form = NewDeviceForm()
        print(form.validate_on_submit())
        print(id)
        devi=Devices.query.get(id)
        print("editng "+str(devi.id))
        
        if form.validate_on_submit():
            devi.hostname=form.hostname.data
            devi.password=form.password.data
            devi.username=form.username.data
            devi.devicetype=form.devicetype.data
            devi.ip=form.ip.data
            db.session.add(devi)
            all=Devices.query.all()
            print(all)
            db.session.commit()
            return redirect(url_for('devices.listdevices'))
        form.devicetype.data=devi.devicetype
        return render_template('edit_device.html',device=devi,form=form)
    else:
        return redirect(url_for("projects.viewid")) 