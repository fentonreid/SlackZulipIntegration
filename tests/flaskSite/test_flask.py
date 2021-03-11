import json
from flaskFiles import app
from pytest import fixture
from flask import url_for, request, session
from os import urandom, environ, getcwd, remove, path
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user
from dotenv import load_dotenv

app.testing = True
app.secret_key = urandom(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///..//tests//testDatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_ENABLED'] = False
login_manager = LoginManager()
login_manager.init_app(app)
db = SQLAlchemy(app)
load_dotenv(dotenv_path="../.env")

# if the testDatabase exists then delete in preparation for testing
if path.exists(getcwd() + r'\flask\testDatabase.db'):
    remove(getcwd() + r'\flask\testDatabase.db')


class User(db.Model, UserMixin):
    """
    User table database structure.

    :param db.model: database model object
    :type db.model: SQLAlchemy database model
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    salt = db.Column(db.LargeBinary(), nullable=False)

    zulipBotRC = db.Column(db.String(), nullable=False, default='NONE')
    zulipAdminRC = db.Column(db.String(), nullable=False, default='NONE')
    slackToken = db.Column(db.String(), nullable=False, default='NONE')
    slackAppToken = db.Column(db.String(), nullable=False, default='NONE')
    slackUserToken = db.Column(db.String(), nullable=False, default='NONE')

    zulipBotRCValidity = db.Column(db.String(), nullable=False, default='Not Uploaded')
    zulipAdminRCValidity = db.Column(db.String(), nullable=False, default='Not Uploaded')
    slackTokenValidity = db.Column(db.String(), nullable=False, default='Not Uploaded')
    slackAppTokenValidity = db.Column(db.String(), nullable=False, default='Not Uploaded')
    slackUserTokenValidity = db.Column(db.String(), nullable=False, default='Not Uploaded')

    slackPrefix = db.Column(db.String(), nullable=False, default='{name} from Zulip |')
    zulipPrefix = db.Column(db.String(), nullable=False, default='{name} from Slack |')
    emojiAdditions = db.Column(db.JSON(), nullable=False, default="{}")

    testMode = db.Column(db.Boolean, default=False, nullable=False)


db.create_all()


@fixture
def client():
    with app.test_client() as test_client: # create a Flask test_client
        with app.app_context(): # persist the app_context
            yield test_client # pass the app context to other functions


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@fixture()
def persistLogin(client):
    # Keep the user logged in
    response = client.post('/login', data={'username': 'test', 'password': 'test'}, follow_redirects=True)

### TEST Non-protected routes
class TestNonProtectedRoutes:
    def test_homeRoute(self, client):
        response = client.get('/')
        assert response.status_code == 200

    def test_signupRoute(self, client):
        response = client.get('/signup')
        assert response.status_code == 200

    def test_loginRoute(self, client):
        response = client.get('/login')
        assert response.status_code == 200

    def test_logout(self, client):
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        assert request.path == url_for("Home")


### TEST Protected Routes
class TestProtectedRoutes():
    def test_API_registerQueue(self, client):
        response = client.get('/api/registerQueue', follow_redirects=True)
        assert request.path == url_for('Home')
        assert b'Unauthorised access' in response.data
        assert response.status_code == 200

    def test_API_registerSocket(self, client):
        response = client.get('/api/registerSocket', follow_redirects=True)
        assert request.path == url_for('Home')
        assert b'Unauthorised access' in response.data
        assert response.status_code == 200

    def test_API_slackEvents(self, client):
        response = client.get('/api/slackEvents', follow_redirects=True)
        assert request.path == url_for('Home')
        assert b'Unauthorised access' in response.data
        assert response.status_code == 200

    def test_API_zulipEvents(self, client):
        response = client.get('/api/zulipEvents', follow_redirects=True)
        assert request.path == url_for('Home')
        assert b'Unauthorised access' in response.data
        assert response.status_code == 200

    def test_integrationDetails(self, client):
        response = client.post('/integrationSetup', follow_redirects=True)
        assert request.path == url_for('Home')
        assert b'Unauthorised access' in response.data
        assert response.status_code == 200

    def test_start(self, client):
        response = client.post('/start', follow_redirects=True)
        assert request.path == url_for('Login')
        assert response.status_code == 200

    def test_settings(self, client):
        response = client.post('/settings', follow_redirects=True)
        assert request.path == url_for('Login')
        assert b'Unauthorised access you need to login first!' in response.data
        assert response.status_code == 200

    def test_settings_view_stored_information(self, client):
        response = client.post('/settings/viewStoredInformation', follow_redirects=True)
        assert request.path == url_for('Login')
        assert b'Unauthorised access you need to login first!' in response.data
        assert response.status_code == 200

    def test_settings_change_password(self, client):
        response = client.post('/settings/changePassword', follow_redirects=True)
        assert request.path == url_for('Login')
        assert b'Unauthorised access you need to login first!' in response.data
        assert response.status_code == 200

    def test_settings_custom_prefix(self, client):
        response = client.post('/settings/customPrefix', follow_redirects=True)
        assert request.path == url_for('Login')
        assert b'Unauthorised access you need to login first!' in response.data
        assert response.status_code == 200

    def test_settings_emoji_additions(self, client):
        response = client.post('/settings/emojiAdditions', follow_redirects=True)
        assert request.path == url_for('Login')
        assert b'Unauthorised access you need to login first!' in response.data
        assert response.status_code == 200

    def test_begin_test(self, client):
        response = client.post('/generateTest', follow_redirects=True)
        assert request.path == url_for('Login')
        assert b'Unauthorised access you need to login first!' in response.data
        assert response.status_code == 200


### TEST Signup
class TestSignup:
    def test_signup_valid(self, client):
        response = client.post('/signup', data={'username' : 'test', 'password' : 'test', 'confirmPassword' : 'test'}, follow_redirects=True)

        assert response.status_code == 200
        assert b'You have successfully signed in' in response.data
        assert request.path == url_for('Login')


    def test_signup_invalid(self, client):
        response = client.post('/signup', data={'username' : 'test', 'password' : 'test', 'confirmPassword' : 'test'}, follow_redirects=True)

        assert response.status_code == 200
        assert b'Username already exists, try logging in!' in response.data
        assert request.path == url_for('Signup')


### TEST Login
class TestLogin:
    def test_login_invalid(self, client):
        response = client.post('/login', data={'username': 'test', 'password': 'no_test'}, follow_redirects=True)

        assert response.status_code == 200
        assert b'Incorrect login credentials, try again!' in response.data
        assert request.path == url_for('Login')


    def test_login_valid(self, client):
        response = client.post('/login', data={'username' : 'test', 'password' : 'test'}, follow_redirects=True)

        assert response.status_code == 200
        assert b'You have successfully logged in!' in response.data
        assert request.path == url_for('IntegrationSetup')


### TEST Integration Protected
class TestProtectedRoutesWithLogin:
    def test_integrationDetails_protected(self, client, persistLogin):
        # ensure that the user is logged in to the protected route i.e. they are successfully logged in
        response = client.post('/integrationSetup')
        assert response.status_code == 200
        assert b'<title>Integration Setup</title>'


    def test_start_protected(self, client, persistLogin):
        response = client.post('/start')
        assert response.status_code == 200
        assert b'<title>Start Integration</title>'


    def test_settings_protected(self, client, persistLogin):
        response = client.post('/settings')
        assert response.status_code == 200
        assert b'<title>Settings</title>'

    def test_settings_view_stored_information_protected(self, client, persistLogin):
        response = client.post('/settings/viewStoredInformation')
        assert response.status_code == 200
        assert b'<title>Stored Data</title>'

    def test_settings_change_password_protected(self, client, persistLogin):
        response = client.post('/settings/changePassword')
        assert response.status_code == 200
        assert b'<title>Change Password</title>'

    def test_settings_custom_prefix_protected(self, client, persistLogin):
        response = client.post('/settings/customPrefix')
        assert response.status_code == 200
        assert b'<title>Initiate Test</title>'

    def test_settings_emoji_additions_protected(self, client, persistLogin):
        response = client.post('/settings/emojiAdditions')
        assert response.status_code == 200
        assert b'<title>Initiate Test</title>'


### TEST SlackApp - Upload and Validation
class Test_slackApp_upload_validation:
    def test_slackApp_upload(self, client, persistLogin):
        response = client.post(url_for('SlackAppToken'), data={'file': 'invalidSlackAppToken', 'hiddenRedirect' : url_for('IntegrationSetup')}, follow_redirects=True)
        # check that the token submitted and redirected back to the integrationSetup page
        assert response.status_code == 200
        assert b'Slack App token submitted successfully' in response.data
        assert request.path == url_for('IntegrationSetup')

        # check the current_user.slackToken to ensure that the slack token was actually saved and the validity is set to not checked
        assert current_user.slackAppToken == 'invalidSlackAppToken'
        assert current_user.slackAppTokenValidity == 'Not Checked'

        # check that the slackToken validity button is set to Not Checked
        assert b'<button id="slackAppTokenSubmit" class="btn btn-sm">Not Checked</button>' in response.data
        db.session.commit()

    def test_slackApp_validate_incorrect_token(self, client, persistLogin):
        response = client.post(url_for('ValidateSlackAppToken'), data={'hiddenRedirect' : url_for('IntegrationSetup')}, follow_redirects=True)

        assert response.status_code == 200
        assert b'Slack App token not valid' in response.data
        assert b'<button id="slackAppTokenSubmit" class="btn btn-sm">Invalid</button>' in response.data
        assert request.path == url_for('IntegrationSetup')

    def test_slackApp_validate_correct_token(self, client, persistLogin):
        # update to a correct Slack App Token based on stored details
        response = client.post(url_for('SlackAppToken'), data={'file': environ.get('slackAppToken'), 'hiddenRedirect' : url_for('IntegrationSetup')}, follow_redirects=True)

        # check that the token submitted and redirected back to the integrationSetup page
        assert response.status_code == 200
        assert b'Slack App token submitted successfully' in response.data
        assert request.path == url_for('IntegrationSetup')
        db.session.commit()

        # validate known working token
        response = client.post(url_for('ValidateSlackAppToken'), data={'hiddenRedirect' : url_for('IntegrationSetup')}, follow_redirects=True)

        assert response.status_code == 200
        assert b'<button id="slackAppTokenSubmit" class="btn btn-sm">Valid</button>' in response.data
        assert request.path == url_for('IntegrationSetup')
        db.session.commit()


### TEST SlackBot - Upload and Validation
class Test_slackBot_upload_validation:
    def test_slackBot_upload(self, client, persistLogin):
        response = client.post(url_for('SlackToken'), data={'file': 'invalidSlackBotToken', 'hiddenRedirect' : url_for('IntegrationSetup')}, follow_redirects=True)

        assert response.status_code == 200
        assert b'Slack Bot token submitted successfully' in response.data
        assert request.path == url_for('IntegrationSetup')
        assert current_user.slackToken == 'invalidSlackBotToken'
        assert current_user.slackTokenValidity == 'Not Checked'
        assert b'<button id="slackBotTokenSubmit" class="btn btn-sm">Not Checked</button>' in response.data
        db.session.commit()


    def test_slackBot_validate_incorrect_token(self, client, persistLogin):
        response = client.post(url_for('ValidateSlackBotToken'), data={'hiddenRedirect' : url_for('IntegrationSetup')}, follow_redirects=True)

        assert response.status_code == 200
        assert b'Slack Bot token not valid' in response.data
        assert b'<button id="slackBotTokenSubmit" class="btn btn-sm">Invalid</button>' in response.data
        assert request.path == url_for('IntegrationSetup')
        db.session.commit()


    def test_slackBot_validate_correct_token(self, client, persistLogin):
        response = client.post(url_for('SlackToken'), data={'file': environ.get('slackToken'), 'hiddenRedirect' : url_for('IntegrationSetup')}, follow_redirects=True)

        assert response.status_code == 200
        assert b'Slack Bot token submitted successfully' in response.data
        assert request.path == url_for('IntegrationSetup')
        db.session.commit()

        response = client.post(url_for('ValidateSlackBotToken'), data={'hiddenRedirect' : url_for('IntegrationSetup')}, follow_redirects=True)

        assert response.status_code == 200
        assert b'<button id="slackBotTokenSubmit" class="btn btn-sm">Valid</button>' in response.data
        assert request.path == url_for('IntegrationSetup')
        db.session.commit()


### TEST SlackUser - Upload and Validation
class Test_slackUser_upload_validation:
    def test_slackUser_upload(self, client, persistLogin):
        response = client.post(url_for('SlackUserToken'), data={'file': 'invalidSlackUserToken', 'hiddenRedirect' : url_for('IntegrationSetup')}, follow_redirects=True)

        assert response.status_code == 200
        assert b'Slack User token submitted successfully' in response.data
        assert request.path == url_for('IntegrationSetup')
        assert current_user.slackUserToken == 'invalidSlackUserToken'
        assert current_user.slackUserTokenValidity == 'Not Checked'
        assert b'<button id="slackUserTokenSubmit" class="btn btn-sm">Not Checked</button>' in response.data
        db.session.commit()


    def test_slackUser_validate_incorrect_token(self, client, persistLogin):
        response = client.post(url_for('ValidateSlackUserToken'), data={'hiddenRedirect' : url_for('IntegrationSetup')}, follow_redirects=True)

        assert response.status_code == 200
        assert b'Slack User token not valid' in response.data
        assert b'<button id="slackUserTokenSubmit" class="btn btn-sm">Invalid</button>' in response.data
        assert request.path == url_for('IntegrationSetup')
        db.session.commit()


    def test_slackUser_validate_correct_token(self, client, persistLogin):
        response = client.post(url_for('SlackUserToken'), data={'file': environ.get('slackUserToken'), 'hiddenRedirect' : url_for('IntegrationSetup')}, follow_redirects=True)

        assert response.status_code == 200
        assert b'Slack User token submitted successfully' in response.data
        assert request.path == url_for('IntegrationSetup')
        db.session.commit()

        response = client.post(url_for('ValidateSlackUserToken'), data={'hiddenRedirect' : url_for('IntegrationSetup')}, follow_redirects=True)

        assert response.status_code == 200
        assert b'<button id="slackUserTokenSubmit" class="btn btn-sm">Valid</button>' in response.data
        assert request.path == url_for('IntegrationSetup')
        db.session.commit()


### TEST ZulipAdmin - Upload and Validation
class Test_zulipAdmin_upload_validation:
    def test_zulipAdmin_upload(self, client, persistLogin):
        with open(getcwd()+r'\zulipAdminTemp.txt','wb') as tempFile:
            tempFile.write(b'invalidAdminText')

        with open(getcwd() + r'\zulipAdminTemp.txt', 'rb') as tempFile:
            response = client.post(url_for('ZulipAdminRC'), data={'file': tempFile, 'hiddenRedirect' : '/integrationSetup'}, follow_redirects=True)
            remove(tempFile.name)

        assert response.status_code == 200
        assert b'.zulipAdminRC file submitted successfully' in response.data
        assert request.path == url_for('IntegrationSetup')

        assert current_user.zulipAdminRC == 'invalidAdminText'
        assert current_user.zulipAdminRCValidity == 'Not Checked'
        assert b'<button id="zulipAdminRCSubmit" class="btn btn-sm">Not Checked</button>' in response.data
        db.session.commit()


    def test_zulipAdminRC_validate_incorrect_token(self, client, persistLogin):
        response = client.post(url_for('ValidateZulipAdminRC'), data={'hiddenRedirect' : url_for('IntegrationSetup')}, follow_redirects=True)

        assert response.status_code == 200
        assert b'.zulipAdminRC not valid' in response.data
        assert b'<button id="zulipAdminRCSubmit" class="btn btn-sm">Invalid</button>' in response.data
        assert request.path == url_for('IntegrationSetup')
        db.session.commit()


    def test_zulipAdminRC_validate_correct_token(self, client, persistLogin):
        with open(getcwd() + r'zulipAdminTemp.txt', 'w') as tempFile:
            tempFile.write(environ.get('zulipAdminRC').replace(r'\n', '\n'))

        with open(getcwd() + r'zulipAdminTemp.txt', 'rb') as tempFile:
            response = client.post(url_for('ZulipAdminRC'), data={'file': tempFile, 'hiddenRedirect' : '/integrationSetup'}, follow_redirects=True)
            remove(tempFile.name)

        assert response.status_code == 200
        assert b'.zulipAdminRC file submitted successfully' in response.data
        assert request.path == url_for('IntegrationSetup')
        db.session.commit()

        response = client.post(url_for('ValidateZulipAdminRC'), data={'hiddenRedirect' : url_for('IntegrationSetup')}, follow_redirects=True)
        assert response.status_code == 200
        assert b'<button id="zulipAdminRCSubmit" class="btn btn-sm">Valid</button>' in response.data
        assert request.path == url_for('IntegrationSetup')
        db.session.commit()


### TEST ZulipBot - Upload and Validation
class Test_zulipBot_upload_validation:
    def test_zulipBot_upload(self, client, persistLogin):
        with open(getcwd() + r'\zulipBotTemp.txt', 'w') as tempFile:
            tempFile.write('invalidBotText')

        with open(getcwd() + r'\zulipBotTemp.txt', 'rb') as tempFile:
            response = client.post(url_for('ZulipBotRC'), data={'file': tempFile, 'hiddenRedirect' : '/integrationSetup'}, follow_redirects=True)
            remove(tempFile.name)

        assert response.status_code == 200
        assert b'.zulipBotRC file submitted successfully' in response.data
        assert request.path == url_for('IntegrationSetup')

        assert current_user.zulipBotRC == 'invalidBotText'
        assert current_user.zulipBotRCValidity == 'Not Checked'
        assert b'<button id="zulipBotRCSubmit" class="btn btn-sm">Not Checked</button>' in response.data
        db.session.commit()

    def test_zulipBotRC_validate_incorrect_token(self, client, persistLogin):
        response = client.post(url_for('ValidateZulipBotRC'), data={'hiddenRedirect' : url_for('IntegrationSetup')}, follow_redirects=True)

        assert response.status_code == 200
        assert b'.zulipBotRC not valid' in response.data
        assert b'<button id="zulipBotRCSubmit" class="btn btn-sm">Invalid</button>' in response.data
        assert request.path == url_for('IntegrationSetup')
        db.session.commit()

    def test_zulipBotRC_validate_correct_token(self, client, persistLogin):
        with open(getcwd() + r'\zulipBotValid.txt', 'w') as tempFile:
            tempFile.write(environ.get('zulipBotRC').replace(r'\n', '\n'))

        with open(getcwd() + r'\zulipBotValid.txt', 'rb') as tempFile:
            response = client.post(url_for('ZulipBotRC'), data={'file': tempFile, 'hiddenRedirect' : url_for('IntegrationSetup')}, follow_redirects=True)
            remove(tempFile.name)


        assert response.status_code == 200
        assert b'.zulipBotRC file submitted successfully' in response.data
        assert request.path == url_for('IntegrationSetup')
        db.session.commit()

        response = client.post(url_for('ValidateZulipBotRC'), data={'hiddenRedirect' : url_for('IntegrationSetup')}, follow_redirects=True)
        assert response.status_code == 200
        assert b'<button id="zulipBotRCSubmit" class="btn btn-sm">Valid</button>' in response.data
        assert request.path == url_for('IntegrationSetup')
        db.session.commit()


## TEST Test Mode -- ensure redirection until enabled via the settings
class TestDisabledTestMode:
    def test_redirection(self, client, persistLogin):
        response = client.get(url_for('RunTests'), follow_redirects=True)

        assert response.status_code == 200
        assert b'Enable testing mode before proceeding!' in response.data
        assert request.path == url_for('Settings')


## TEST Settings -- Protected Routes
class TestSettingsWithLogin:
    def test_view_stored_information_with_login(self, client, persistLogin):
        response = client.get(url_for('ViewStoredInformation'))
        assert response.status_code == 200
        assert request.path == url_for('ViewStoredInformation')

    def test_change_password_with_login(self, client, persistLogin):
        response = client.get(url_for('ChangePassword'))
        assert response.status_code == 200
        assert request.path == url_for('ChangePassword')

    def test_custom_prefix_with_login(self, client, persistLogin):
        response = client.get(url_for('CustomMessagePrefix'))
        assert response.status_code == 200
        assert request.path == url_for('CustomMessagePrefix')


### TEST Enable Test Mode
class TestEnableTestMode:
    def test_enableTestMode(self, client, persistLogin):
        response = client.post(url_for('Settings'), data={'testModeCheckbox' : 1, 'nameOfForm' : 'testMode'})
        assert response.status_code == 200
        assert request.path == url_for('Settings')
        assert b'<a class="form-inline mr-5" href="/generateTest">Run Tests</a>' in response.data
        assert current_user.testMode
        db.session.commit()


### TEST Routes -- Protected Routes because of missing uploads and validation (all stored information up to this point is valid)
class TestRoutesProtectedFromMissingInformation:
    def test_runTests(self, client, persistLogin):
        response = client.get(url_for('RunTests'))
        assert response.status_code == 200
        assert request.path == url_for('RunTests')
        assert b'<button onclick="document.getElementById(\'acceptBox\').checked = false;" type="submit" class="btn btn-info" id="runTestButton">Run Tests' in response.data


    def test_startIntegration(self, client, persistLogin):
        response = client.get(url_for('Start'))
        assert response.status_code == 200
        assert request.path == url_for('Start')
        assert b'<button onclick="startIntegration()" id="startButton" type="submit" class="btn btn-lg btn-success" style="width: 15%; height: 6%;">Start' in response.data and b'<button onclick="stopIntegration()" id="stopButton" type="button" class="btn btn-lg btn-danger" style="width: 15%; height: 6%;">Stop</button>' in response.data


### TEST View Stored Information
class TestStoredInformation:
    def test_stored_information_values(self, client, persistLogin):
        response = client.get(url_for('ViewStoredInformation'))
        assert response.status_code == 200
        assert request.path == url_for('ViewStoredInformation')

        ## check that all Stored Integration Data fields are displaying the correct information and are valid
        assert b'<label>Username: <input class="form-control" type="text" placeholder="test" readonly></label>' in response.data # Username
        assert b'<input id="slackAppTokenInput" class="form-control" type="text" onmouseleave="onmouseOff(\'slackAppTokenInput\')" onmouseover="onmouseOn(\'slackAppTokenInput\', \'' + environ.get('slackAppToken').encode() + b'\')" placeholder="*************" readonly></td>\n                    <td>\n                        \n                        Yes' in response.data # Slack App Token
        assert b'<input id="slackTokenInput" class="form-control" type="text" onmouseleave="onmouseOff(\'slackTokenInput\')" onmouseover="onmouseOn(\'slackTokenInput\', \'' + environ.get('slackToken').encode() + b'\')" placeholder="*************" readonly></td>\n                    <td>\n                        \n                        Yes' in response.data # Slack Bot Token
        assert b'<input id="slackUserTokenInput" class="form-control" type="text" onmouseleave="onmouseOff(\'slackUserTokenInput\')" onmouseover="onmouseOn(\'slackUserTokenInput\', \'' + environ.get('slackUserToken').encode() + b'\')" placeholder="*************" readonly></td>\n                    <td>\n                        \n                        Yes' in response.data # Slack User Token
        assert b'<input id="zulipAdminRCInput" class="form-control" type="text" onmouseleave="onmouseOff(\'zulipAdminRCInput\')" onmouseover="onmouseOn(\'zulipAdminRCInput\', \'' + environ.get('zulipAdminRC').replace(r'\n', ' ').encode() + b'\')" placeholder="*************" readonly></td>\n                    <td>\n                        \n                        Yes' in response.data # Zulip Admin RC
        assert b'<input id="zulipBotRCInput" class="form-control" type="text" onmouseleave="onmouseOff(\'zulipBotRCInput\')" onmouseover="onmouseOn(\'zulipBotRCInput\', \'' + environ.get('zulipBotRC').replace(r'\n', ' ').encode() + b'\')" placeholder="*************" readonly></td>\n                    <td>\n                        \n                        Yes' in response.data # Zulip Bot RC

    def test_stored_information_uploads(self, client, persistLogin):
        ## upload Stored Information and then check against table
        # Slack App Token
        response = client.post(url_for('SlackAppToken'), data={'file': 'invalidSlackAppToken', 'hiddenRedirect': url_for('ViewStoredInformation')}, follow_redirects=True)
        assert response.status_code == 200
        assert b'Slack App token submitted successfully' in response.data
        assert request.path == url_for('ViewStoredInformation')
        assert current_user.slackAppToken == 'invalidSlackAppToken'
        assert current_user.slackAppTokenValidity == 'Not Checked'
        assert b'<input id="slackAppTokenInput" class="form-control" type="text" onmouseleave="onmouseOff(\'slackAppTokenInput\')" onmouseover="onmouseOn(\'slackAppTokenInput\', \'' + current_user.slackAppToken.encode() + b'\')" placeholder="*************" readonly></td>\n                    <td>\n                        \n                        No' in response.data

        ## Slack Bot Token
        response = client.post(url_for('SlackToken'), data={'file': 'invalidSlackBotToken', 'hiddenRedirect': url_for('ViewStoredInformation')}, follow_redirects=True)
        assert response.status_code == 200
        assert b'Slack Bot token submitted successfully' in response.data
        assert request.path == url_for('ViewStoredInformation')
        assert current_user.slackToken == 'invalidSlackBotToken'
        assert current_user.slackTokenValidity == 'Not Checked'
        assert b'<input id="slackTokenInput" class="form-control" type="text" onmouseleave="onmouseOff(\'slackTokenInput\')" onmouseover="onmouseOn(\'slackTokenInput\', \'' + current_user.slackToken.encode() + b'\')" placeholder="*************" readonly></td>\n                    <td>\n                        \n                        No' in response.data

        ## Slack User Token
        response = client.post(url_for('SlackUserToken'), data={'file': 'invalidSlackUserToken', 'hiddenRedirect': url_for('ViewStoredInformation')}, follow_redirects=True)
        assert response.status_code == 200
        assert b'Slack User token submitted successfully' in response.data
        assert request.path == url_for('ViewStoredInformation')
        assert current_user.slackUserToken == 'invalidSlackUserToken'
        assert current_user.slackUserTokenValidity == 'Not Checked'
        assert b'<input id="slackUserTokenInput" class="form-control" type="text" onmouseleave="onmouseOff(\'slackUserTokenInput\')" onmouseover="onmouseOn(\'slackUserTokenInput\', \'' + current_user.slackUserToken.encode() + b'\')" placeholder="*************" readonly></td>\n                    <td>\n                        \n                        No' in response.data

        ## Zulip Admin RC
        with open(getcwd() + r'zulipAdminTemp.txt', 'w') as tempFile:
            tempFile.write('invalidAdminText')

        with open(getcwd() + r'zulipAdminTemp.txt', 'rb') as tempFile:
            response = client.post(url_for('ZulipAdminRC'), data={'file': tempFile, 'hiddenRedirect' : url_for('ViewStoredInformation')}, follow_redirects=True)
            remove(tempFile.name)

        assert response.status_code == 200
        assert b'.zulipAdminRC file submitted successfully' in response.data
        assert request.path == url_for('ViewStoredInformation')

        assert current_user.zulipAdminRC == 'invalidAdminText'
        assert current_user.zulipAdminRCValidity == 'Not Checked'
        assert b'<input id="zulipAdminRCInput" class="form-control" type="text" onmouseleave="onmouseOff(\'zulipAdminRCInput\')" onmouseover="onmouseOn(\'zulipAdminRCInput\', \'' + current_user.zulipAdminRC.encode() + b'\')" placeholder="*************" readonly></td>\n                    <td>\n                        \n                        No' in response.data

        ## Zulip Bot RC
        with open(getcwd() + r'zulipBotTemp.txt', 'w') as tempFile:
            tempFile.write('invalidBotText')

        with open(getcwd() + r'zulipBotTemp.txt', 'rb') as tempFile:
            response = client.post(url_for('ZulipBotRC'), data={'file': tempFile, 'hiddenRedirect': url_for('ViewStoredInformation')}, follow_redirects=True)
            remove(tempFile.name)

        assert response.status_code == 200
        assert b'.zulipBotRC file submitted successfully' in response.data
        assert request.path == url_for('ViewStoredInformation')

        assert current_user.zulipBotRC == 'invalidBotText'
        assert current_user.zulipBotRCValidity == 'Not Checked'
        assert b'<input id="zulipBotRCInput" class="form-control" type="text" onmouseleave="onmouseOff(\'zulipBotRCInput\')" onmouseover="onmouseOn(\'zulipBotRCInput\', \'' + current_user.zulipBotRC.encode() + b'\')" placeholder="*************" readonly></td>\n                    <td>\n                        \n                        No' in response.data
        db.session.commit()


### TEST Change Password
class TestChangePassword:
    def test_incorrect_old_password(self, client, persistLogin):
        previousHash = current_user.password
        previousSalt = current_user.salt
        response = client.post(url_for('ChangePassword'), data={'oldPassword': 'not_old_password', 'password' : 'newPassword', 'confirmPassword' : 'newPassword'})

        assert response.status_code == 200
        assert request.path == url_for('ChangePassword')
        assert b'The old password was not correct!' in response.data
        assert previousHash == current_user.password
        assert previousSalt == current_user.salt


    def test_not_equal_passwords(self, client, persistLogin):
        previousHash = current_user.password
        previousSalt = current_user.salt
        response = client.post(url_for('ChangePassword'), data={'oldPassword': 'test', 'password': 'password1', 'confirmPassword': 'password2'})

        assert response.status_code == 200
        assert request.path == url_for('ChangePassword')
        assert b'Passwords did not match, try again!' in response.data
        assert previousHash == current_user.password
        assert previousSalt == current_user.salt


    def test_valid_password(self, client, persistLogin):
        previousHash = current_user.password
        previousSalt = current_user.salt
        response = client.post(url_for('ChangePassword'), data={'oldPassword': 'test', 'password': 'newPassword', 'confirmPassword': 'newPassword'}, follow_redirects=True)

        assert response.status_code == 200
        assert request.path == url_for('Settings')
        assert b'Password successfully changed!' in response.data
        assert previousHash != current_user.password
        assert previousSalt != current_user.salt
        db.session.commit()

        # logout and try the new login
        response = client.get(url_for('Logout'), follow_redirects=True)
        assert response.status_code == 200 and request.path == url_for('Home')
        assert session.get('slackPrefix') is None and session.get('zulipPrefix') is None
        assert not current_user.is_authenticated

        response = client.post('/login', data={'username' : 'test', 'password' : 'newPassword'}, follow_redirects=True)
        assert response.status_code == 200 and request.path == url_for('IntegrationSetup')
        assert current_user.is_authenticated

        #change the user back
        client.post(url_for('ChangePassword'), data={'oldPassword': 'newPassword', 'password': 'test', 'confirmPassword': 'test'}, follow_redirects=True)
        db.session.commit()


### TEST Message Prefixes
class TestMessagePrefixes:
    def test_message_prefixes_defaults(self, client, persistLogin):
        response = client.get(url_for('CustomMessagePrefix'))
        # the default Slack and Zulip prefix is assigned
        assert response.status_code == 200 and request.path == url_for('CustomMessagePrefix')
        assert current_user.slackPrefix == '{name} from Zulip |' and session['slackPrefix'] == '{name} from Zulip |'
        assert current_user.zulipPrefix == '{name} from Slack |' and session['zulipPrefix'] == '{name} from Slack |'

        # the slack field has the default text
        assert b'<input id="slackInput" name="slackInput" oninput="displayFormatting(&#39;slackInput&#39;, &#39;slackOutput&#39;)" style="width: 400px;" type="text" value="' + session['slackPrefix'].encode() + b'">' in response.data
        assert b'<input id="zulipInput" name="zulipInput" oninput="displayFormatting(&#39;zulipInput&#39;, &#39;zulipOutput&#39;)" style="width: 400px;" type="text" value="' + session['zulipPrefix'].encode() + b'">' in response.data

    def test_update_slack_zulip_prefix(self, client, persistLogin):
        response = client.post(url_for('CustomMessagePrefix'), data={'slackHidden' : '{email} 📢 to {channel} from Zulip >', 'zulipHidden' : '{email} 💬 to {channel} from Slack>'}, follow_redirects=True)
        assert response.status_code == 200 and request.path == url_for('Settings')

        # check that the prefixes updated in the database and session
        assert current_user.slackPrefix == '{email} 📢 to {channel} from Zulip >' and session['slackPrefix'] == '{email} 📢 to {channel} from Zulip >'
        assert current_user.zulipPrefix == '{email} 💬 to {channel} from Slack>' and session['zulipPrefix'] == '{email} 💬 to {channel} from Slack>'
        assert b'Custom prefixes adjusted successfully' in response.data

        # check the Custom Message page to ensure the fields contain the newest prefixes
        response = client.get(url_for('CustomMessagePrefix'))
        assert response.status_code == 200 and request.path == url_for('CustomMessagePrefix')

        assert b'<input id="slackInput" name="slackInput" oninput="displayFormatting(&#39;slackInput&#39;, &#39;slackOutput&#39;)" style="width: 400px;" type="text" value="' + session['slackPrefix'].replace('>', '&gt;').encode() + b'">' in response.data
        assert b'<input id="zulipInput" name="zulipInput" oninput="displayFormatting(&#39;zulipInput&#39;, &#39;zulipOutput&#39;)" style="width: 400px;" type="text" value="' + session['zulipPrefix'].replace('>', '&gt;').encode() + b'">' in response.data
        db.session.commit()


### TEST Emoji Additions
class TestEmojiAdditions:
    def test_emoji_additions_defaults(self, client, persistLogin):
        response = client.get(url_for('EmojiAdditions'))
        assert response.status_code == 200 and request.path == url_for('EmojiAdditions')
        assert current_user.emojiAdditions == "{}"

    def test_emoji_additions_add_new_entry(self, client, persistLogin):
        response = client.post(url_for('EmojiAdditions'), data={"add" : "yes", "addSlack" : ":heart:", "addZulip" : ":heart:"})
        assert response.status_code == 200 and request.path == url_for('EmojiAdditions')

        # ensure that the emoji was added successfully to the current_user.emojiAdditions row
        assert current_user.emojiAdditions == json.dumps({":heart:" : ":heart:"})
        db.session.commit()

    def test_emoji_additions_duplicates(self, client, persistLogin):
        response = client.post(url_for('EmojiAdditions'), data={"add": "yes", "addSlack" : ":heart:", "addZulip" : ":duplicate:"})
        assert response.status_code == 200 and request.path == url_for('EmojiAdditions')
        # ensure that emojiAdditions is unchanged
        assert current_user.emojiAdditions == json.dumps({":heart:" : ":heart:"})

        response = client.post(url_for('EmojiAdditions'), data={"add": "yes", "addSlack" : ":duplicate:", "addZulip" : ":heart:"})
        assert response.status_code == 200 and request.path == url_for('EmojiAdditions')
        assert current_user.emojiAdditions == json.dumps({":heart:" : ":heart:"})
        db.session.commit()

    def test_emoji_additions_remove_entry(self, client, persistLogin):
        response = client.post(url_for('EmojiAdditions'),  data={"remove": "yes", "removeSlack" : ":heart:", "removeZulip" : ":heart:"})
        assert response.status_code == 200 and request.path == url_for('EmojiAdditions')
        # ensure that the heart emoji mapping is removed
        assert current_user.emojiAdditions == "{}"


### TEST Delete Stored Integration Details
class TestDeleteStoredIntegrationDetails:
    def test_delete_stored_integration_details(self, client, persistLogin):
        response = client.post(url_for('Settings'), data={'nameOfForm' : 'deleteDetails'})
        assert response.status_code == 200 and request.path == url_for('Settings')

        # ensure all details are deleted and that the session prefixes are restored to default
        assert current_user.slackAppToken == 'NONE' and current_user.slackToken == 'NONE' and current_user.slackUserToken == 'NONE' and current_user.zulipAdminRC == 'NONE' and current_user.zulipBotRC == 'NONE'
        assert current_user.slackAppTokenValidity == 'Not Uploaded' and current_user.slackTokenValidity == 'Not Uploaded' and current_user.slackUserTokenValidity == 'Not Uploaded' and  current_user.zulipAdminRCValidity == 'Not Uploaded' and current_user.zulipBotRCValidity == 'Not Uploaded'
        assert current_user.slackPrefix == '{name} from Zulip |' and session['slackPrefix'] == '{name} from Zulip |'
        assert current_user.zulipPrefix == '{name} from Slack |' and session['zulipPrefix'] == '{name} from Slack |'
        db.session.commit()


### TEST Routes -- Missing Upload(s) and Validate Upload(s)
class TestMissingData:
    def test_runTests(self, client, persistLogin):
        response = client.get(url_for('RunTests'))
        assert response.status_code == 200 and request.path == url_for('RunTests')
        assert b'<p class="h3">Missing Upload(s)</p>\n        <div class="list-group list-group-flush">\n            \n                \n                    <a href="/integrationSetup/slackAppToken" class="list-group-item list-group-item-action" style="width: 25%;">Slack App Token</a>\n                \n            \n                \n                    <a href="/integrationSetup/slackBotToken" class="list-group-item list-group-item-action" style="width: 25%;">Slack Bot Token</a>\n                \n            \n                \n                    <a href="/integrationSetup/slackUserToken" class="list-group-item list-group-item-action" style="width: 25%;">Slack User Token</a>\n                \n            \n                \n                    <a href="/integrationSetup/zulipAdminRC" class="list-group-item list-group-item-action" style="width: 25%;">Zulip Admin RC</a>\n                \n            \n                \n                    <a href="/integrationSetup/zulipBotRC" class="list-group-item list-group-item-action" style="width: 25%;">Zulip Bot RC</a>' in response.data
        assert b'<p class="h3">Validate Upload(s)</p>' not in response.data

        ## ensure that after each upload the missing upload is removed
        # Slack App Token
        response = client.post(url_for('SlackAppToken'), data={'file': environ.get('slackAppToken'), 'hiddenRedirect' : url_for('RunTests')}, follow_redirects=True)
        assert response.status_code == 200 and request.path == url_for('RunTests')
        assert current_user.slackAppTokenValidity == 'Not Checked' and current_user.slackAppToken == environ.get('slackAppToken') and b'Slack App token submitted successfully' in response.data

        response = client.get(url_for('RunTests'))
        assert response.status_code == 200 and request.path == url_for('RunTests')
        assert b'<p class="h3">Missing Upload(s)</p>\n        <div class="list-group list-group-flush">\n            \n                \n            \n                \n                    <a href="/integrationSetup/slackBotToken" class="list-group-item list-group-item-action" style="width: 25%;">Slack Bot Token</a>\n                \n            \n                \n                    <a href="/integrationSetup/slackUserToken" class="list-group-item list-group-item-action" style="width: 25%;">Slack User Token</a>\n                \n            \n                \n                    <a href="/integrationSetup/zulipAdminRC" class="list-group-item list-group-item-action" style="width: 25%;">Zulip Admin RC</a>\n                \n            \n                \n                    <a href="/integrationSetup/zulipBotRC" class="list-group-item list-group-item-action" style="width: 25%;">Zulip Bot RC</a>' in response.data
        assert b'<p class="h3">Validate Upload(s)</p>\n        <div class="list-group list-group-flush">\n            \n                    \n                        <form method="POST" action="/integrationSetup/validate/slackAppToken" style="margin-bottom: 0;">\n                            <button type="submit" class="list-group-item list-group-item-action a" style="width: 25%;cursor: auto; border-top: 0; border-left: 0; border-right: 0; outline: none;">Slack App Token</button>' in response.data

        # Slack Bot Token
        response = client.post(url_for('SlackToken'), data={'file': environ.get('slackToken'), 'hiddenRedirect': url_for('RunTests')}, follow_redirects=True)
        assert response.status_code == 200 and request.path == url_for('RunTests')
        assert current_user.slackTokenValidity == 'Not Checked' and current_user.slackToken == environ.get('slackToken') and b'Slack Bot token submitted successfully' in response.data

        response = client.get(url_for('RunTests'))
        assert response.status_code == 200 and request.path == url_for('RunTests')
        assert b'<p class="h3">Missing Upload(s)</p>\n        <div class="list-group list-group-flush">\n            \n                \n            \n                \n            \n                \n                    <a href="/integrationSetup/slackUserToken" class="list-group-item list-group-item-action" style="width: 25%;">Slack User Token</a>\n                \n            \n                \n                    <a href="/integrationSetup/zulipAdminRC" class="list-group-item list-group-item-action" style="width: 25%;">Zulip Admin RC</a>\n                \n            \n                \n                    <a href="/integrationSetup/zulipBotRC" class="list-group-item list-group-item-action" style="width: 25%;">Zulip Bot RC</a>\n                \n            \n        </div>\n    </div>\n    <br><br>\n\n\n    <br>\n    <div class="container">'
        assert b'<p class="h3">Validate Upload(s)</p>\n        <div class="list-group list-group-flush">\n            \n                    \n                        <form method="POST" action="/integrationSetup/validate/slackAppToken" style="margin-bottom: 0;">\n                            <button type="submit" class="list-group-item list-group-item-action a" style="width: 25%;cursor: auto; border-top: 0; border-left: 0; border-right: 0; outline: none;">Slack App Token</button>\n                        </form>\n                    \n            \n                    \n                        <form method="POST" action="/integrationSetup/validate/slackBotToken" style="margin-bottom: 0;">\n                            <button type="submit" class="list-group-item list-group-item-action a" style="width: 25%;cursor: auto; border-top: 0; border-left: 0; border-right: 0; outline: none;">Slack Bot Token</button>' in response.data

        # Slack User Token
        response = client.post(url_for('SlackUserToken'),  data={'file': environ.get('slackUserToken'), 'hiddenRedirect': url_for('RunTests')},  follow_redirects=True)
        assert response.status_code == 200 and request.path == url_for('RunTests')
        assert current_user.slackUserTokenValidity == 'Not Checked' and current_user.slackUserToken == environ.get('slackUserToken') and b'Slack User token submitted successfully' in response.data

        response = client.get(url_for('RunTests'))
        assert response.status_code == 200 and request.path == url_for('RunTests')
        assert b'<p class="h3">Missing Upload(s)</p>\n        <div class="list-group list-group-flush">\n            \n                \n            \n                \n            \n                \n            \n                \n                    <a href="/integrationSetup/zulipAdminRC" class="list-group-item list-group-item-action" style="width: 25%;">Zulip Admin RC</a>\n                \n            \n                \n                    <a href="/integrationSetup/zulipBotRC" class="list-group-item list-group-item-action" style="width: 25%;">Zulip Bot RC</a>\n                \n            \n        </div>\n    </div>\n    <br><br>\n\n\n    <br>\n    <div class="container">' in response.data
        assert b'<p class="h3">Validate Upload(s)</p>\n        <div class="list-group list-group-flush">\n            \n                    \n                        <form method="POST" action="/integrationSetup/validate/slackAppToken" style="margin-bottom: 0;">\n                            <button type="submit" class="list-group-item list-group-item-action a" style="width: 25%;cursor: auto; border-top: 0; border-left: 0; border-right: 0; outline: none;">Slack App Token</button>\n                        </form>\n                    \n            \n                    \n                        <form method="POST" action="/integrationSetup/validate/slackBotToken" style="margin-bottom: 0;">\n                            <button type="submit" class="list-group-item list-group-item-action a" style="width: 25%;cursor: auto; border-top: 0; border-left: 0; border-right: 0; outline: none;">Slack Bot Token</button>\n                        </form>\n                    \n            \n                    \n                        <form method="POST" action="/integrationSetup/validate/slackUserToken" style="margin-bottom: 0;">\n                            <button type="submit" class="list-group-item list-group-item-action a" style="width: 25%;cursor: auto; border-top: 0; border-left: 0; border-right: 0; outline: none;">Slack User Token</button>' in response.data

        # Zulip Admin RC
        with open(getcwd()+r'zulipAdminTemp.txt','wb') as tempFile:
            tempFile.write(environ.get('zulipAdminRC').replace(r'\n', '\n').encode())

        with open(getcwd() + r'zulipAdminTemp.txt', 'rb') as tempFile:
            response = client.post(url_for('ZulipAdminRC'), data={'file': tempFile, 'hiddenRedirect' : url_for('RunTests')}, follow_redirects=True)
            remove(tempFile.name)

        assert current_user.zulipAdminRC == environ.get('zulipAdminRC').replace(r'\n', ' ') and current_user.zulipAdminRCValidity == 'Not Checked' and b'.zulipAdminRC file submitted successfully' in response.data

        response = client.get(url_for('RunTests'))
        assert response.status_code == 200 and request.path == url_for('RunTests')
        assert b'<p class="h3">Missing Upload(s)</p>\n        <div class="list-group list-group-flush">\n            \n                \n            \n                \n            \n                \n            \n                \n            \n                \n                    <a href="/integrationSetup/zulipBotRC" class="list-group-item list-group-item-action" style="width: 25%;">Zulip Bot RC</a>\n                \n            \n        </div>\n    </div>\n    <br><br>\n\n\n    <br>\n    <div class="container">' in response.data
        assert b'<p class="h3">Validate Upload(s)</p>\n        <div class="list-group list-group-flush">\n            \n                    \n                        <form method="POST" action="/integrationSetup/validate/slackAppToken" style="margin-bottom: 0;">\n                            <button type="submit" class="list-group-item list-group-item-action a" style="width: 25%;cursor: auto; border-top: 0; border-left: 0; border-right: 0; outline: none;">Slack App Token</button>\n                        </form>\n                    \n            \n                    \n                        <form method="POST" action="/integrationSetup/validate/slackBotToken" style="margin-bottom: 0;">\n                            <button type="submit" class="list-group-item list-group-item-action a" style="width: 25%;cursor: auto; border-top: 0; border-left: 0; border-right: 0; outline: none;">Slack Bot Token</button>\n                        </form>\n                    \n            \n                    \n                        <form method="POST" action="/integrationSetup/validate/slackUserToken" style="margin-bottom: 0;">\n                            <button type="submit" class="list-group-item list-group-item-action a" style="width: 25%;cursor: auto; border-top: 0; border-left: 0; border-right: 0; outline: none;">Slack User Token</button>\n                        </form>\n                    \n            \n                    \n                        <form method="POST" action="/integrationSetup/validate/zulipAdminRC" style="margin-bottom: 0;">\n                            <button type="submit" class="list-group-item list-group-item-action a" style="width: 25%;cursor: auto; border-top: 0; border-left: 0; border-right: 0; outline: none;">Zulip Admin RC</button>' in response.data

        # Zulip Bot RC
        with open(getcwd()+r'zulipBotTemp.txt','wb') as tempFile:
            tempFile.write(environ.get('zulipBotRC').replace(r'\n', '\n').encode())

        with open(getcwd() + r'zulipBotTemp.txt', 'rb') as tempFile:
            response = client.post(url_for('ZulipBotRC'), data={'file': tempFile, 'hiddenRedirect' : url_for('RunTests')}, follow_redirects=True)
            remove(tempFile.name)

        assert current_user.zulipBotRC == environ.get('zulipBotRC').replace(r'\n', ' ') and current_user.zulipBotRCValidity == 'Not Checked' and b'.zulipBotRC file submitted successfully' in response.data

        response = client.get(url_for('RunTests'))
        assert response.status_code == 200 and request.path == url_for('RunTests')
        assert b'<p class="h3">Missing Upload(s)</p>' not in response.data
        assert b'<p class="h3">Validate Upload(s)</p>\n        <div class="list-group list-group-flush">\n            \n                    \n                        <form method="POST" action="/integrationSetup/validate/slackAppToken" style="margin-bottom: 0;">\n                            <button type="submit" class="list-group-item list-group-item-action a" style="width: 25%;cursor: auto; border-top: 0; border-left: 0; border-right: 0; outline: none;">Slack App Token</button>\n                        </form>\n                    \n            \n                    \n                        <form method="POST" action="/integrationSetup/validate/slackBotToken" style="margin-bottom: 0;">\n                            <button type="submit" class="list-group-item list-group-item-action a" style="width: 25%;cursor: auto; border-top: 0; border-left: 0; border-right: 0; outline: none;">Slack Bot Token</button>\n                        </form>\n                    \n            \n                    \n                        <form method="POST" action="/integrationSetup/validate/slackUserToken" style="margin-bottom: 0;">\n                            <button type="submit" class="list-group-item list-group-item-action a" style="width: 25%;cursor: auto; border-top: 0; border-left: 0; border-right: 0; outline: none;">Slack User Token</button>\n                        </form>\n                    \n            \n                    \n                        <form method="POST" action="/integrationSetup/validate/zulipAdminRC" style="margin-bottom: 0;">\n                            <button type="submit" class="list-group-item list-group-item-action a" style="width: 25%;cursor: auto; border-top: 0; border-left: 0; border-right: 0; outline: none;">Zulip Admin RC</button>\n                        </form>\n                    \n            \n                    \n                        <form method="POST" action="/integrationSetup/validate/zulipBotRC" style="margin-bottom: 0;">\n                            <button type="submit" class="list-group-item list-group-item-action a" style="width: 25%;cursor: auto; border-top: 0; border-left: 0; border-right: 0; outline: none;">Zulip Bot RC</button>' in response.data

        ## Validate all files and ensure the user has access to the RunTests endpoint without missing information
        # Validate SlackAppToken
        response = client.post(url_for('ValidateSlackAppToken'), data={'hiddenRedirect' : url_for('RunTests')}, follow_redirects=True)
        assert response.status_code == 200 and request.path == url_for('RunTests')
        assert current_user.slackAppTokenValidity == 'Valid'

        # Validate SlackToken
        response = client.post(url_for('ValidateSlackBotToken'), data={'hiddenRedirect' : url_for('RunTests')}, follow_redirects=True)
        assert response.status_code == 200 and request.path == url_for('RunTests') and current_user.slackTokenValidity == 'Valid'

        # Validate SlackUserToken
        response = client.post(url_for('ValidateSlackUserToken'), data={'hiddenRedirect' : url_for('RunTests')}, follow_redirects=True)
        assert response.status_code == 200 and request.path == url_for('RunTests') and current_user.slackUserTokenValidity == 'Valid'

        # Validate ZulipAdminRC
        response = client.post(url_for('ValidateZulipAdminRC'), data={'hiddenRedirect' : url_for('RunTests')}, follow_redirects=True)
        assert response.status_code == 200 and request.path == url_for('RunTests') and current_user.zulipAdminRCValidity == 'Valid'

        # Validate ZulipBotRC
        response = client.post(url_for('ValidateZulipBotRC'), data={'hiddenRedirect' : url_for('RunTests')}, follow_redirects=True)
        assert response.status_code == 200 and request.path == url_for('RunTests') and current_user.zulipBotRCValidity == 'Valid'

        # Missing Upload or Validate upload should not be present in the page now
        response = client.get(url_for('RunTests'))
        assert response.status_code == 200 and request.path == url_for('RunTests')
        assert b'<p class="h3">Missing Upload(s)</p>' not in response.data
        assert b'<p class="h3">Validate Upload(s)</p>' not in response.data


    def test_startIntegration(self, client, persistLogin):
        # All tokens are missing data
        response = client.get(url_for('Start'))
        assert response.status_code == 200 and request.path == url_for('Start')
        assert b'<p class="h3">Missing Upload(s)</p>\n        <div class="list-group list-group-flush">\n            \n                \n                    <a href="/integrationSetup/slackAppToken" class="list-group-item list-group-item-action" style="width: 25%;">Slack App Token</a>\n                \n            \n                \n                    <a href="/integrationSetup/slackBotToken" class="list-group-item list-group-item-action" style="width: 25%;">Slack Bot Token</a>\n                \n            \n                \n                    <a href="/integrationSetup/slackUserToken" class="list-group-item list-group-item-action" style="width: 25%;">Slack User Token</a>\n                \n            \n                \n                    <a href="/integrationSetup/zulipAdminRC" class="list-group-item list-group-item-action" style="width: 25%;">Zulip Admin RC</a>\n                \n            \n                \n                    <a href="/integrationSetup/zulipBotRC" class="list-group-item list-group-item-action" style="width: 25%;">Zulip Bot RC</a>' in response.data

        ## All tokens are needing validated
        current_user.slackAppTokenValidity = current_user.slackTokenValidity = current_user.slackUserTokenValidity = current_user.zulipAdminRCValidity = current_user.zulipBotRCValidity = "Invalid"

        response = client.get(url_for('Start'))
        assert b'<p class="h3">Missing Upload(s)</p>' not in response.data
        assert b'<p class="h3">Validate Upload(s)</p>\n        <div class="list-group list-group-flush">\n            \n                    \n                        <form method="POST" action="/integrationSetup/validate/slackAppToken" style="margin-bottom: 0;">\n                            <button type="submit" class="list-group-item list-group-item-action a" style="width: 25%;cursor: auto; border-top: 0; border-left: 0; border-right: 0; outline: none;">Slack App Token</button>\n                        </form>\n                    \n            \n                    \n                        <form method="POST" action="/integrationSetup/validate/slackBotToken" style="margin-bottom: 0;">\n                            <button type="submit" class="list-group-item list-group-item-action a" style="width: 25%;cursor: auto; border-top: 0; border-left: 0; border-right: 0; outline: none;">Slack Bot Token</button>\n                        </form>\n                    \n            \n                    \n                        <form method="POST" action="/integrationSetup/validate/slackUserToken" style="margin-bottom: 0;">\n                            <button type="submit" class="list-group-item list-group-item-action a" style="width: 25%;cursor: auto; border-top: 0; border-left: 0; border-right: 0; outline: none;">Slack User Token</button>\n                        </form>\n                    \n            \n                    \n                        <form method="POST" action="/integrationSetup/validate/zulipAdminRC" style="margin-bottom: 0;">\n                            <button type="submit" class="list-group-item list-group-item-action a" style="width: 25%;cursor: auto; border-top: 0; border-left: 0; border-right: 0; outline: none;">Zulip Admin RC</button>\n                        </form>\n                    \n            \n                    \n                        <form method="POST" action="/integrationSetup/validate/zulipBotRC" style="margin-bottom: 0;">\n                            <button type="submit" class="list-group-item list-group-item-action a" style="width: 25%;cursor: auto; border-top: 0; border-left: 0; border-right: 0; outline: none;">Zulip Bot RC</button>' in response.data


        ## Tokens uploaded and validated
        current_user.slackAppTokenValidity = current_user.slackTokenValidity = current_user.slackUserTokenValidity = current_user.zulipAdminRCValidity = current_user.zulipBotRCValidity = "Valid"

        response = client.get(url_for('Start'))
        assert response.status_code == 200 and request.path == url_for('Start')
        assert b'<p class="h3">Missing Upload(s)</p>' not in response.data
        assert b'<p class="h3">Validate Upload(s)</p>' not in response.data


### TEST Delete Account
class TestDeleteAccount:
    def test_deleteAccount(self, client, persistLogin):
        response = client.post(url_for('Settings'), data={'nameOfForm' : 'deleteAccount'}, follow_redirects=True)
        assert response.status_code == 200 and request.path == url_for('Home')
        assert not current_user.is_authenticated

        # Login with deleted account
        response = client.post('/login', data={'username' : 'test', 'password' : 'test'})
        assert response.status_code == 200 and request.path == url_for('Login')
        assert not current_user.is_authenticated
        assert b'Incorrect login credentials, try again!' in response.data