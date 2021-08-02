from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,TextAreaField
from wtforms.validators import DataRequired

class NewProjectForm(FlaskForm):
   # document = FileField('Document', validators=[FileRequired(), FileAllowed(['xls', 'xlsx'], 'Excel Document only!')])
    name = StringField('Project name' ,validators=[DataRequired()])
    description = TextAreaField('Project Description',validators=[DataRequired()])
 

    submit = SubmitField('Create New Project')


class NewFolderForm(FlaskForm):
   # document = FileField('Document', validators=[FileRequired(), FileAllowed(['xls', 'xlsx'], 'Excel Document only!')])
    name = StringField('SubProject name', validators=[DataRequired()])
    description = TextAreaField('SubProject Description',validators=[DataRequired()])
 

    submit = SubmitField('Create New SubProject')