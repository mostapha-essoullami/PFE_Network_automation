from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, TextAreaField
from wtforms.validators import DataRequired

class CreateForm(FlaskForm):
    playname = StringField('Name')
    ansibleplay= TextAreaField(validators=[DataRequired()])
    submit = SubmitField('Save')

class EditForm(FlaskForm):
    ansibleplay= TextAreaField(validators=[DataRequired()])
    submit = SubmitField('Edit')