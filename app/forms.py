from flask_wtf import Form
from wtforms import StringField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired



class xForm(Form):
    subject = StringField('subject')
    body = StringField('body')
    submit = SubmitField('Send Emails')
    subject = StringField('Title')
    body = TextAreaField('txteditor')

def __init__(self):
    Form.__init__(self)