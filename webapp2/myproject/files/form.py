from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, TextAreaField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import DataRequired

class DocumentUploadForm(FlaskForm):
   # document = FileField('Document', validators=[FileRequired(), FileAllowed(['xls', 'xlsx'], 'Excel Document only!')])
    csvdoc = FileField('csv configuration', validators=[FileRequired()])
    jinjadoc = FileField('Jinja configuration template')
    submit = SubmitField('Upload')

class EditForm(FlaskForm):

    jinjafile= TextAreaField(validators=[DataRequired()])
    submit = SubmitField('Edit')