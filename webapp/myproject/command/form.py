from flask_wtf import FlaskForm
from wtforms import widgets, SubmitField, SelectField, SelectMultipleField, RadioField, TextAreaField
from wtforms.validators import DataRequired



class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class DeviceForm(FlaskForm):
    devices=MultiCheckboxField('Label',coerce=str)
    execmode = RadioField('Label', coerce=str, choices=[('0','Global Configuration Mode'),('1','Privileged Mode')])
    command= TextAreaField(validators=[DataRequired()])
    submit = SubmitField('SEND')