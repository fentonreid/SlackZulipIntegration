from wtforms import StringField, PasswordField, SubmitField, HiddenField, BooleanField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, EqualTo


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirmPassword = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class ChangePasswordForm(FlaskForm):
    oldPassword = PasswordField('Old Password', validators=[DataRequired()])
    password = PasswordField('New Password', validators=[DataRequired()])
    confirmPassword = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Change')


class SlackUserTokenForm(FlaskForm):
    slackUserTokenFile = StringField('Slack User Token', validators=[DataRequired()])
    hiddenRedirect = HiddenField()
    submit = SubmitField('Save')

class UploadForm(FlaskForm):
    file = StringField('', validators=[DataRequired()])
    hiddenRedirect = HiddenField()
    submit = SubmitField('Upload')


class DeleteAccountForm(FlaskForm):
    nameOfForm = HiddenField("")
    submit = SubmitField()


class MessagePrefixForm(FlaskForm):
    slackHidden = HiddenField('')
    zulipHidden = HiddenField('')

    slackInput = StringField('')
    zulipInput = StringField('')


class DeleteDetailsForm(FlaskForm):
    nameOfForm = HiddenField("")
    submit = SubmitField()


class TestModeForm(FlaskForm):
    nameOfForm = HiddenField("")
    testModeCheckbox = BooleanField()
    submit = SubmitField()


class StartTestForm(FlaskForm):
    submit = SubmitField()