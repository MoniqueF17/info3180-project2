from app.models import Posts, UserProfile, Likes, Follows
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators, ValidationError
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import DataRequired, Email

class CreateUserForm(FlaskForm):
    fName = StringField('First Name', [validators.Length(min=1, max=80)])

    lName = StringField('Last Name', [validators.Length(min=1, max=80)])
    
    uName = StringField('Username', [validators.Length(min=1, max=80)])
    
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.Length(max=70),
        validators.EqualTo('confirm', message='Passwords must match')
    ])

    confirm = PasswordField('Confirm Password',[
        validators.DataRequired(),
        validators.Length(max=70),
        validators.EqualTo('password', message='Passwords must match')])
        
    email = StringField('Email', validators=[DataRequired(), Email()])
    
    loc = StringField('Location', [validators.Length(min=1, max=140)])
    
    bio = StringField('(Optional) Profile Bio', validators=[validators.Length(min=0, max=140)])
    
    imgfile = FileField('(Optional) Upload a Profile Picture')

    FormSubmitted = False

    def validate_userName(self, form, field):
        user = UserProfile.query.filter_by(username=field.data).first()
        if user is not None: # Username already exist so we cannot proceed safely
            raise ValidationError('Username already exists.')

class LoginForm(FlaskForm):
    uName = StringField('Username', validators=[validators.DataRequired()])
    password = PasswordField('Password', validators=[validators.DataRequired()])

class CreatPostForm(FlaskForm):
    photo = FileField('Photo', validators=[FileRequired(),
        FileAllowed(['jpg', 'png', 'Images only!'])
    ])
    
    cap = StringField('Caption', validators=[DataRequired()])
