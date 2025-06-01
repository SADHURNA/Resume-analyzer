from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed

class ResumeUploadForm(FlaskForm):
    resume = FileField('Upload Resume', validators=[
        DataRequired(),
        FileAllowed(['pdf', 'docx'], 'Only PDF and DOCX files are allowed!')
    ])
    submit = SubmitField('Upload')
