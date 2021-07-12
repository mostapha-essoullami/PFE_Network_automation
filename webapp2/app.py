from myproject import app
from flask import render_template, redirect, url_for
from myproject.models import Project, Folder, Logs, Devices

@app.route('/')
def index():
 
    return redirect(url_for('projects.listprojects'))

if __name__=='__main__':
    app.run(host='0.0.0.0',debug=True)