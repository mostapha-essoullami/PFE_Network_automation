
from flask_wtf import FlaskForm
from wtforms import widgets,StringField, SubmitField, SelectField
from wtforms.validators import DataRequired


class NewDeviceForm(FlaskForm):
   # document = FileField('Document', validators=[FileRequired(), FileAllowed(['xls', 'xlsx'], 'Excel Document only!')])
    hostname = StringField('Hostname')
    username = StringField('Username', validators=[DataRequired()])
    ip = StringField('IP Address', validators=[DataRequired()])
    password = StringField('Password')
    devicetype = SelectField('Device Type',choices=[("cisco_ios","cisco ios"),("cisco_nxos","cisxo nxos")],coerce=str)
    submit = SubmitField('Add Device')
