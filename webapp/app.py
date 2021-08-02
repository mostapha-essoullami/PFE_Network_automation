from myproject import app
from flask import redirect, url_for


@app.route('/')
def index():
 
    return redirect(url_for('projects.listprojects'))

if __name__=='__main__':
    app.run(host='0.0.0.0',debug=True)