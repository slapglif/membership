from flask_wtf import Form
from wtforms import StringField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired



class xForm(Form):
    submit = SubmitField('Send Emails')
    subject = StringField('Title')
    body = TextAreaField('txteditor')


class fdlform(Form):
    clientname = StringField("Client Name")
    clientpw = StringField("Client PW")
    submit = SubmitField('Send Emails')

def __init__(self):
    Form.__init__(self)