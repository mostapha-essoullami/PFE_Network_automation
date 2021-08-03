from flask import Blueprint, Flask, render_template, redirect, url_for, request
from myproject.files.form import DocumentUploadForm,EditForm
from myproject.projects.view import folderpath,subprojectselected
from werkzeug.utils import secure_filename
import os
from myproject.models import  Devices, ConfigFiles
import jinja2
from myproject import db, tftp_path

files_blueprint= Blueprint('files',__name__,template_folder="templates")


def rename(filepath, new_name):
    parent, _ = os.path.split(filepath)
    new_filepath = os.path.join(parent, new_name)
    print("renaming", filepath, new_filepath)
    os.rename(filepath, new_filepath)

    
def createconf(template_file,csv_parameter_file):
    config_parameters = []
   # output_directory = os.path.join(folderpath(), 'config-files')
    subproject_id=int(request.cookies.get('subproject_id'))
    # 1. read the contents from the CSV files
    print("Read CSV parameter file...")
    f = open(os.path.join(folderpath(), 'csv',csv_parameter_file))
    csv_content = f.read()
    f.close()

    # 2. for Jinja2, we need to convert the given CSV file into the a python
    # dictionary to get the script a bit more reusable, I will not statically
    # limit the possible header values (and therefore the variables)
    print("Convert CSV file to dictionaries...")
    csv_lines = csv_content.splitlines()
    headers = csv_lines[0].split(",")
    

    for i in range(1, len(csv_lines)):
        values = csv_lines[i].split(",")
        parameter_dict = dict()
        if len(values)==len(headers):
            for h in range(0, len(headers)):
                parameter_dict[headers[h]] = values[h]
            config_parameters.append(parameter_dict)
        else:
            print("your csv need more values")
    print(headers)
    deviceinfo=["username","password","devicetype"]
    autoadddevice=True
    for info in deviceinfo:
        if info not in headers:
            autoadddevice=False
            break
    if autoadddevice:
        print("adding device")
        
        hostexist=False
        ipexist=False
        if "hostname" in headers:
            hostexist=True
        if "ip" in headers:
            ipexist=True
        for parameter in config_parameters:
            hostname=""
            ip="0.0.0.0"
            if hostexist:
                hostname=parameter["hostname"]
            if ipexist:
                ip=parameter["ip"]
            dev=Devices(hostname,ip,parameter["username"],parameter["password"],parameter["devicetype"],subproject_id)
            db.session.add(dev)
            f=open(os.path.join(folderpath(),"ansible","hosts"),"r+")
            originalContent = f.read()
            f.seek(0, 0)
            f.write(dev.devicetype+str(dev.id)+"\n")
            f.write(originalContent)
            f.close()
            f=open(os.path.join(folderpath(),"ansible","host_vars",dev.devicetype+str(dev.id)+".yml"),"w+")
            f.write("ansible_host: "+dev.ip+"\nansible_connection: network_cli \nansible_network_os: ios \nansible_become: yes \nansible_become_method: enable \nansible_user: "+dev.username+" \nansible_ssh_pass: "+dev.password)
            f.close()
        db.session.commit()
    # 3. next we need to create the central Jinja2 environment and we will load
    # the Jinja2 template file
    print("Create Jinja2 environment...")
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath=os.path.join(folderpath(), 'jinja')))
    template = env.get_template(template_file)

    # we will make sure that the output directory exists
  #  if not os.path.exists(output_directory):
   #     os.mkdir(output_directory)

    # 4. now create the templates
    print("Create templates...")
    for parameter in config_parameters:
        result = template.render(parameter)
        #write to local

  #      f = open(os.path.join(output_directory, parameter['serial'] + ".config"), "w")
   #     f.write(result)
    #    f.close()

        #write to tftp path
        f = open(os.path.join(tftp_path, parameter['serial'] + ".config"), "w")
        f.write(result)
        f.close()
        
        file=ConfigFiles(parameter['serial'] + ".config",subproject_id)
        db.session.add(file)
            
        print("Configuration '%s' created..." % (parameter['serial'] + ".config"))
    db.session.commit()
    print("DONE")

@files_blueprint.route('/jinja/<file>', methods=['GET', 'POST'])
def jinjaread(file):
    if subprojectselected():
        form = EditForm()
        print(file)
        print(form.validate_on_submit())
        path= os.path.join(folderpath(), 'jinja',file)
        f=open(path,'r')
        aa=f.read()
        f.close()
        print(aa)
        print("editng "+str(file))
        if form.validate_on_submit():
            print(form.jinjafile.data)
            f=open(path,'w')
            f.writelines(form.jinjafile.data.split("\r"))
            f.close()
            return redirect(url_for('files.listtemplates'))
        form.jinjafile.data=aa
        
        return render_template('editjinja.html',form=form,file=file)
    else:
        return redirect(url_for("projects.viewid"))    

@files_blueprint.route('/deletejinja/<file>')
def deletejinja(file):
    if subprojectselected():
        path= os.path.join(folderpath(), 'jinja',file)

        print("removing "+str(file))
        os.remove(path)

        return redirect(url_for('files.listtemplates'))
    else:
        return redirect(url_for("projects.viewid"))  

@files_blueprint.route('/confiles')
def listconfs():
    if subprojectselected():
       # path= os.path.join(folderpath(), 'config-files')
        
        subproject_id=int(request.cookies.get('subproject_id'))
        ConfigFiles.query.filter_by(subproject_id=subproject_id)
       # files=os.listdir(path)
        confiles=ConfigFiles.query.filter_by(subproject_id=subproject_id)
        
        return render_template('confFiles.html',confiles=confiles)
    else:
        return redirect(url_for("projects.viewid"))  

@files_blueprint.route('/deleteconf/<id>')
def deleteconf(id):
    if subprojectselected():
       # path= os.path.join(folderpath(), 'config-files',file)
        
        #print("removing "+str(file))
      #  os.remove(path)
        file=ConfigFiles.query.get(id)
        os.remove(os.path.join(tftp_path,file.name))

        
       
        db.session.delete(file)
        db.session.commit()
        return redirect(url_for('files.listconfs'))
    else:
        return redirect(url_for("projects.viewid"))  

@files_blueprint.route('/conf/<file>', methods=['GET', 'POST'])
def confread(file):
    if subprojectselected():
        form = EditForm()
        print(file)
        print(form.validate_on_submit())
        pathtftp= os.path.join(tftp_path,file)
        f=open(pathtftp,'r')
        aa=f.read()
        f.close()
        print(aa)
        print("editng "+str(file))
        if form.validate_on_submit():
            print("********")
          

            f=open(pathtftp,'w')
            print(repr(form.jinjafile.data))
            f.writelines(form.jinjafile.data.split("\r"))
            f.close()
            return redirect(url_for('files.listconfs'))
        form.jinjafile.data=aa
        
        return render_template('editconf.html',form=form,file=file)
    else:
        return redirect(url_for("projects.viewid"))  


@files_blueprint.route('/uploadconf', methods=['GET', 'POST'])
def upload():
    if subprojectselected():
        form = DocumentUploadForm()
        path= os.path.join(folderpath(), 'jinja')

        print(path)
        print("*******")
        print(form.validate_on_submit())
        print("+++++")
        if form.validate_on_submit():
            print("-----")
            filename,csvfilename="",""
            if form.jinjadoc.data:
                uploaded_file = form.jinjadoc.data
                filename = secure_filename(uploaded_file.filename )
                print(filename)

                if filename != '':
                    uploaded_file.save(os.path.join(path,filename))
            print("SSSSS")
            print("-----")

            uploaded_file = form.csvdoc.data
            if uploaded_file:
                csvfilename = secure_filename(uploaded_file.filename )
                print(filename)
                
                if csvfilename != '':
                    uploaded_file.save(os.path.join(os.path.join(folderpath(), 'csv'),csvfilename))
        # print(form.profile.raw_data[0].read())
            if filename!='' and csvfilename!='':
                createconf(filename,csvfilename)
            else:
                print("non nno nn o")
            return redirect(url_for('projects.dashboard'))

        return render_template('upload_conf.html',form=form)
    else:
        return redirect(url_for("projects.viewid"))  
@files_blueprint.route('/templates')
def listtemplates():
    if subprojectselected():
        path= os.path.join(folderpath(), 'jinja')
        files=os.listdir(path)
        print(files)
        return render_template('listjinja.html',files=files)
    else:
        return redirect(url_for("projects.viewid")) 