from flask_wtf import Form
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class xForm(Form):
    ign = StringField('ign')
    community = StringField('community')
    email = StringField('email')
    age = StringField('name')
    search = StringField('search')
    submit = SubmitField('Submit Application!')


