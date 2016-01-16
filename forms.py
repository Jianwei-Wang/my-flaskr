from flask_wtf import Form
from wtforms import StringField, TextAreaField, SubmitField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, Length, Regexp
from flask.ext.pagedown.fields import PageDownField

class RegisteForm(Form):
    username = StringField('username', validators = [DataRequired()])
    email = StringField('username', validators = [DataRequired(), Email()])
    password = PasswordField('password', validators = [DataRequired()])
    confirm = PasswordField('confirm', validators = [DataRequired()])
    submit = SubmitField('submit')

class LoginForm(Form):
    name = StringField('name', validators = [DataRequired()])
    password = PasswordField('password', validators = [DataRequired()])
    submit = SubmitField('submit')


class ComposeForm(Form):
    title = StringField('title')
    body = PageDownField("What's on your mind?", validators=[DataRequired()])
    submit = SubmitField('Submit')

class ProfileForm(Form):
    real_name = StringField('Real name', validators = [Length(0, 64)])
    location = StringField('Location', validators = [Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

class EditProfileAdminForm(Form):
    name = StringField('Real name', validators = [DataRequired(), Length(1, 64),
                                                  Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                  'Usernames must have only letters'
                                                  'numbers, dots or underscores')])
    email = StringField('Email', validators = [DataRequired(), Length(1, 64), Email()])
    real_name = StringField('Real name', validators = [Length(0, 64)])
    location = StringField('Location', validators = [Length(0, 64)])
    about_me = TextAreaField('About me')
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce = int)
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        from models import Role
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email = field.data).first():
            raise ValidationError('Email already Registered.')

    def validate_username(self, field):
        if field.data != self.user.name and User.query.filter_by(name = field.data).first():
            raise ValidatationError('Username already in use.')
