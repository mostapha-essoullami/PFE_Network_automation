from flask import Blueprint, Flask, render_template, redirect, url_for, request
from myproject.command.form import DeviceForm
from myproject.models import Devices, Logs
from myproject import db
from myproject.projects.view import subprojectselected
from multiprocessing.dummy import Pool as ThreadPool
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException
from paramiko.ssh_exception import SSHException
from netmiko.ssh_exception import AuthenticationException
from itertools import repeat
command_blueprint= Blueprint('command',__name__,template_folder="templates")

def executecmd(device,cmds,mode):
    global outputs
    status="Success"
    message="No Errors"
    output=""
    climode="mode"
    print ('Connecting to device" ' + device.ip)
    
    ios_device = {
        'device_type': device.devicetype,
        'ip': device.ip, 
        'username': device.username,
        'password': device.password
    }

    try:
        net_connect = ConnectHandler(**ios_device)
        if mode=='0':
            climode="config mode"
            output = net_connect.send_config_set(cmds)
        else:
            climode="enable mode"
            for command in cmds:
                out = net_connect.send_command(command)
                
                output+=command+'\n'+out
        print (output)
    except (AuthenticationException):
        message="Authentication failure to "+device.ip
        print(message)
        status="Failed"
 
        
    except (NetMikoTimeoutException):
        message='Timeout to device: ' +device.ip
        print(message)
   
        status="Failed"
    except (EOFError):
        message='End of file while attempting device ' +device.ip
        print(message)
 
        status="Failed"  
    except (SSHException):
        message='SSH Issue. Are you sure SSH is enabled? '+device.ip
        print(message)
  
        status="Failed"
    except Exception as unknown_error:
        message='Some other error: ' + str(unknown_error)
        print(message)
  
        status="Failed" 

    finally:
        net_connect.disconnect()

        log=Logs(device.hostname,device.ip,device.devicetype,device.subproject_id,status,climode,message,str(cmds))
        db.session.add(log)
        db.session.commit()

        outputs.append({"hostname":device.hostname,"ip":device.ip,"status":status,"mode":climode,"message":message,"output":output})
        

outputs=[]
@command_blueprint.route('/sendcmd', methods=['GET', 'POST'])
def sendcmd():
    global outputs
    if subprojectselected():
        form = DeviceForm()
        subprojectid=int(request.cookies.get('subproject_id'))
        all=Devices.query.filter_by(subproject_id=subprojectid)
        form.devices.choices=[('0',"Check All")]+[(str(i.id),i.hostname+" |"+i.ip) for i in all]

        if form.validate_on_submit():
            print("valid")
            print(form.devices.data)
            print(form.execmode.data)
            print("***")
            print(form.command.data.splitlines())

            selected=[]
            
            outputs=[]
            if '0' in form.devices.data:
                selected=all
            else:
                for device in all:
                    if str(device.id) in form.devices.data:
                        selected.append(device)

            num_threads=5
            threads = ThreadPool( num_threads )
            commands=form.command.data.splitlines()
            results = threads.map( executecmd, zip(selected, repeat(commands),repeat(form.execmode.data) ))

            
            threads.close()
            threads.join()
            print(results)

      #      for device in selected:

       #         outputs.append(executecmd(device,form.command.data.splitlines(),form.execmode.data))

            return render_template("results.html",outputs=outputs)

        return render_template("sendcmd.html", form=form,total_log=1,mode='Command Line')
    else:
        return redirect(url_for("projects.viewid"))


@command_blueprint.route('/logs', methods=['GET', 'POST'])
def showlogs():
    if subprojectselected():
        
        subprojectid=int(request.cookies.get('subproject_id'))
        

        logs=Logs.query.filter_by(subproject_id=subprojectid).order_by(Logs.time.desc())
        return render_template("logs.html", logs=logs)
    else:
        return redirect(url_for("projects.viewid"))


