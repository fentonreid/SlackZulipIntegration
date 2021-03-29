from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from flask_login import LoginManager
from flaskFiles.forms import *
from json import dumps, load, loads
from os import urandom, getcwd, chdir, remove, system
from pytest import main
from flask import Flask, render_template, flash, url_for, redirect, session, request, send_from_directory
from flask_login import current_user, login_user, logout_user
from hashlib import sha512
from requests import post, get
from flaskFiles.forms import *
from integration.events.slackEvents import slackEvents
from integration.events.zulipEvents import zulipEvents
from integration.markdown.emojis.shortCodeDict import emojiList
from integration.reportGeneration.parseReport import parseReport
from integration.utilities import parseZulipRC, slackHeader


app = Flask(__name__)
app.secret_key = urandom(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///userDetails.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(minutes=60)
login_manager = LoginManager()
login_manager.init_app(app)
db = SQLAlchemy(app)

from flaskFiles.table import User

db.create_all()


@login_manager.user_loader
def load_user(user_id):
    """
    :param user_id: Unique ID of the logged in user
    :return: Integer
    """
    # get the user_id of the saved user
    return User.query.get(user_id)


@app.route('/')
def Home():
    return render_template('home.html')


@app.route('/testing/test.txt')
def TestTxt():
    return send_from_directory("static", "test.txt")


@app.route('/api/validate', methods=[ 'GET', 'POST'])
def SlackValidateEndPoint():
    if request.method == 'POST':
        slackIncoming = request.json
        if 'challenge' in slackIncoming:
            return slackIncoming['challenge']
    return ''


@app.route('/login', methods=['GET', 'POST'])
def Login():
    if current_user.is_authenticated:
        flash("You are already logged in!", 'warning')
        return redirect(url_for("IntegrationSetup"))

    loginForm = LoginForm()

    if loginForm.username.data is not None and loginForm.password.data is not None:
        if len(loginForm.username.data) < 2:
            flash("Username must be longer than one character, try again!", 'warning')
            return render_template('login.html', form=loginForm)

    if loginForm.validate_on_submit():
        # check user against database
        foundUser = db.session.query(User).filter_by(username=loginForm.username.data).first()

        # if user is not found then flash an error
        if foundUser is None:
            flash("Incorrect login credentials, try again!", 'warning')
            return render_template('login.html', form=loginForm)

        # hash the users password and check against the database stored hash
        hashCheck = sha512(loginForm.password.data.encode() + foundUser.salt).hexdigest()

        if hashCheck == foundUser.password:
            # add the logged in user to the session
            login_user(foundUser)
            db.session.commit()

            # add slack and zulip prefix session data
            session['slackPrefix'] = current_user.slackPrefix
            session['zulipPrefix'] = current_user.zulipPrefix

            flash("You have successfully logged in!", 'success')
            return redirect(url_for('IntegrationSetup'))
        else:
            flash("Incorrect login credentials, try again!", 'warning')

    return render_template('login.html', form=loginForm)



@app.route('/signup', methods=('GET', 'POST'))
def Signup():
    if current_user.is_authenticated:
        flash("You are already logged in!", 'warning')
        return redirect(url_for('Home'))

    signupForm = SignupForm()

    # check if both passwords match
    if signupForm.password.data is not None and signupForm.confirmPassword.data is not None:
        if len(signupForm.username.data) < 2:
            flash("Username must be longer than one character, try again", 'warning')
            return render_template('signup.html', form=signupForm)

        if signupForm.password.data != signupForm.confirmPassword.data:
            flash("Password did not match, try again", 'warning')
            return render_template('signup.html', form=signupForm)

    if signupForm.validate_on_submit():
        # check if user exists already
        if len(db.session.query(User).filter_by(username=signupForm.username.data).all()) > 0:
            flash("Username already exists, try logging in!", 'danger')
            return render_template('signup.html', form=signupForm)

        # store hash and salt in database
        salt = urandom(16)
        secureHash = sha512(signupForm.password.data.encode() + salt).hexdigest()
        newUser = User(username=signupForm.username.data, password=secureHash, salt=salt)

        db.session.add(newUser)
        db.session.commit()

        flash("You have successfully signed in", 'success')
        return redirect(url_for('Login'))

    return render_template('signup.html', form=signupForm)


@app.route('/api/registerQueue', methods=['GET', 'POST'])
def RegisterQueue():
    if current_user.is_authenticated:
        if request.method == 'POST':
            # make a request to the Zulip endpoint and return back
            zulipAuth = parseZulipRC(current_user.zulipBotRC)
            registerQueue = {"narrow": '[["stream", "Slack"]]'}

            result = post(zulipAuth['site'] + "/api/v1/register", auth=(zulipAuth['email'], zulipAuth['key']), data=registerQueue)
            if result.status_code == 200:
                result = result.json()
                if 'result' in result and result['result'] == 'success' and 'queue_id' in result:
                    return dumps({'queue_id' : result['queue_id']}), 200
            return dumps({"error": "encountered an error"}), 419

    flash("Unauthorised access", 'danger')
    return redirect(url_for("Home"))


@app.route('/api/registerSocket', methods=['GET', 'POST'])
def RegisterSocket():
    if current_user.is_authenticated:
        if request.method == 'POST':
            # register a Slack socket using current user data
            openConnectionRequest = post("https://slack.com/api/apps.connections.open", headers=slackHeader(current_user.slackAppToken))

            if openConnectionRequest.status_code == 200:
                openConnectionRequest = openConnectionRequest.json()
                # send back to JavaScript handler if the request is valid
                if 'ok' in openConnectionRequest and openConnectionRequest['ok'] and 'url' in openConnectionRequest and len(openConnectionRequest['url']) > 0:
                    return dumps({'socketURL' : openConnectionRequest['url']}), 200
            return dumps({"error": "encountered an error"}), 419

    flash("Unauthorised access", 'danger')
    return redirect(url_for("Home"))


@app.route('/generateTest', methods=['GET', 'POST'])
def RunTests():
    if current_user.is_authenticated:
        if request.method == 'GET':
            # if test mode is enabled by the user
            if current_user.testMode == 1:
                form = StartTestForm()
                return render_template("startTest.html", form=form)
            else:
                flash('Enable testing mode before proceeding!', 'warning')
                return redirect(url_for("Settings"))

        elif request.method == 'POST':
            # change to the tests directory
            originalDir = getcwd()
            jsonFile = originalDir + r"/generated/" + str(current_user.id) + "Report.json"
            chdir("../tests")

            # run the integration tests
            main(["integration/", "-s", "-q", "--no-header", "--no-summary", "--tb=no", f"--json={jsonFile}"])

            # reset to ensure if tests are written again the directory is not affected
            chdir(originalDir)

            # remove the users report
            reportJSON = load(open(f"{jsonFile}", "r"))
            remove(jsonFile)

            # parse the test results and pass to the template
            reportObject = parseReport(reportJSON)
            reportObject.generate()

            return render_template("generatedReport.html", reportObject=reportObject)

    flash("Unauthorised access you need to login first!", 'warning')
    return redirect(url_for("Login"))


@app.route('/start', methods=['GET', 'POST'])
def Start():
    if current_user.is_authenticated:
        return render_template("startIntegration.html", zulipAuth=parseZulipRC(current_user.zulipBotRC))

    flash("Unauthorised access you need to login first", 'warning')
    return redirect(url_for("Login"))


@app.route('/api/slackEvents', methods=['GET', 'POST'])
def slackEventRoute():
    """
    All incoming Slack Events are processed further by the slackEvents file.
    Incoming Slack Events are generally passed from the JavaScript handler to here.
    """
    if current_user.is_authenticated:
        if request.method == 'POST':
            if 'event' in request.json:
                slackEvents(request.json['event'])
            return "Authorised"

    flash("Unauthorised access", 'danger')
    return redirect(url_for("Home"))


@app.route('/api/zulipEvents', methods=['GET', 'POST'])
def zulipEventRoute():
    """
    All Zulip events that are received via HTTP POST requests are sent to this endpoint and processed further.
    Incoming Zulip events are generally passed from the JavaScript handler to here.
    """
    if current_user.is_authenticated:
        if request.method == 'POST':
            if 'result' in request.json and request.json['result'] == 'success':
                zulipEvents(request.json['events'])
        return "Authorised"

    flash("Unauthorised access", 'danger')
    return redirect(url_for("Home"))


@app.route('/settings', methods=['GET', 'POST'])
def Settings():
    if current_user.is_authenticated:
        deleteAccountForm = DeleteAccountForm()
        deleteDetailsForm = DeleteDetailsForm()
        testModeForm = TestModeForm()

        if request.method == 'GET':
            return render_template('settings.html', testModeForm=testModeForm, deleteAccountForm=deleteAccountForm, deleteDetailsForm=deleteDetailsForm)

        elif request.method == 'POST':
            if testModeForm.validate_on_submit() and testModeForm.nameOfForm.data == 'testMode':
                current_user.testMode = testModeForm.testModeCheckbox.data
                db.session.commit()

            if deleteDetailsForm.validate_on_submit() and deleteDetailsForm.nameOfForm.data == 'deleteDetails':
                # give default values to all user stored credentials
                current_user.slackToken = 'NONE'
                current_user.zulipBotRC = 'NONE'
                current_user.zulipAdminRC = 'NONE'
                current_user.slackAppToken = 'NONE'
                current_user.slackUserToken = 'NONE'

                current_user.slackPrefix = '{name} from Zulip |'
                current_user.zulipPrefix = '{name} from Slack |'

                session['slackPrefix'] = '{name} from Zulip |'
                session['zulipPrefix'] = '{name} from Slack |'

                current_user.zulipBotRCValidity = 'Not Uploaded'
                current_user.zulipAdminRCValidity = 'Not Uploaded'
                current_user.slackTokenValidity = 'Not Uploaded'
                current_user.slackAppTokenValidity = 'Not Uploaded'
                current_user.slackUserTokenValidity = 'Not Uploaded'

                db.session.commit()

                flash("Integration Details deleted successfully", 'success')
                return render_template("settings.html", testModeForm=testModeForm, deleteAccountForm=deleteAccountForm, deleteDetailsForm=deleteDetailsForm)

            if deleteAccountForm.validate_on_submit() and deleteAccountForm.nameOfForm.data == 'deleteAccount':
                # delete the users account
                db.session.query(User).filter_by(username=current_user.username).delete()
                db.session.commit()
                logout_user()

                flash("Account was deleted successfully!", 'success')
                return redirect(url_for('Home'))

            return render_template("settings.html", testModeForm=testModeForm, deleteAccountForm=deleteAccountForm, deleteDetailsForm=deleteDetailsForm)


    flash("Unauthorised access you need to login first!", 'warning')
    return redirect(url_for('Login'), )


@app.route('/settings/emojiAdditions', methods=['GET', 'POST'])
def EmojiAdditions():
    if current_user.is_authenticated:
        current_user.emojiAdditions = loads(current_user.emojiAdditions)
        if request.method == "POST":
            if request.form.get('remove') == "yes":
                if request.form.get('removeSlack') in current_user.emojiAdditions:
                    current_user.emojiAdditions.pop(request.form.get('removeSlack'))
                    current_user.emojiAdditions = current_user.emojiAdditions

            elif request.form.get('add') == 'yes':
                if request.form.get('addSlack') not in current_user.emojiAdditions and request.form.get('addSlack') not in current_user.emojiAdditions.values() and request.form.get('addZulip') not in current_user.emojiAdditions and request.form.get('addZulip') not in current_user.emojiAdditions.values():
                    current_user.emojiAdditions[request.form.get('addSlack')] = request.form.get('addZulip')
                    flash("Added successfully!", "success")
                else:
                    flash("Emoji already mapped!", "warning")

        # convert to string representation of dictionary
        current_user.emojiAdditions = dumps(current_user.emojiAdditions)
        db.session.commit()
        return render_template('emojiAdditions.html', emoji=loads(current_user.emojiAdditions))

    flash("Unauthorised access you need to login first!", 'warning')
    return redirect(url_for('Login'))


@app.route('/settings/customPrefix', methods=['GET', 'POST'])
def CustomMessagePrefix():
    if current_user.is_authenticated:
        customMessagePrefix = MessagePrefixForm()
        
        if customMessagePrefix.validate_on_submit():
            # custom checking on the prefix data
            if customMessagePrefix.slackHidden.data is not None and customMessagePrefix.zulipHidden.data is not None:
                # update database and session data
                current_user.slackPrefix = customMessagePrefix.slackHidden.data
                current_user.zulipPrefix = customMessagePrefix.zulipHidden.data

                session['slackPrefix'] = customMessagePrefix.slackHidden.data
                session['zulipPrefix'] = customMessagePrefix.zulipHidden.data
                db.session.commit()

                flash('Custom prefixes adjusted successfully', 'success')
                return redirect(url_for('Settings'))

            else:
                flash('Seems like something went wrong, try again!', 'warning')
                return render_template('customPrefix.html', emojiList=emojiList(), form=customMessagePrefix)
        return render_template('customPrefix.html', emojiList=emojiList(), form=customMessagePrefix)

    flash("Unauthorised access you need to login first!", 'warning')
    return redirect(url_for("Login"))


@app.route('/settings/changePassword', methods=['GET', 'POST'])
def ChangePassword():
    if current_user.is_authenticated:
        changePasswordForm = ChangePasswordForm()

        if changePasswordForm.oldPassword.data is not None and changePasswordForm.password.data is not None and changePasswordForm.confirmPassword.data is not None:
            if changePasswordForm.password.data != changePasswordForm.confirmPassword.data:
                flash("Passwords did not match, try again!", 'danger')
                return render_template('changePassword.html', form=changePasswordForm)

        if changePasswordForm.validate_on_submit():
            foundUser = db.session.query(User).filter_by(username=current_user.username).first()

            if foundUser is None:
                flash("Unauthorised access", 'danger')
                return redirect(url_for("Home"))

            # check the old password matches before changing the new one
            hashCheck = sha512(changePasswordForm.oldPassword.data.encode() + foundUser.salt).hexdigest()

            if hashCheck == foundUser.password:
                # update the users password and salt into the database
                salt = urandom(16)
                secureHash = sha512(changePasswordForm.password.data.encode() + salt).hexdigest()
                current_user.password = secureHash
                current_user.salt = salt
                db.session.commit()

                flash("Password successfully changed!", 'success')
                return redirect(url_for('Settings'))

            else:
                flash("The old password was not correct!", 'danger')
                return render_template('changePassword.html', form=changePasswordForm)

        else:
            return render_template('changePassword.html', form=changePasswordForm)

    flash("Unauthorised access you need to login first!", 'warning')
    return redirect(url_for('Login'))


@app.route('/settings/viewStoredInformation',  methods=['GET', 'POST'])
def ViewStoredInformation():
    if current_user.is_authenticated:
        return render_template("viewStoredInformation.html")

    flash("Unauthorised access you need to login first!", 'warning')
    return redirect(url_for('Login'))


@app.route('/integrationSetup/validate/slackAppToken', methods=['GET', 'POST'])
def ValidateSlackAppToken():
    if request.method == "POST":
        current_user.slackAppTokenValidity = "Invalid"
        try:
            appTestRequest = post("https://slack.com/api/apps.connections.open", headers=slackHeader(current_user.slackAppToken))
            appTestRequest = appTestRequest.json()

            if appTestRequest['ok'] and 'error' not in appTestRequest:
                current_user.slackAppTokenValidity = "Valid"

            elif 'error' in appTestRequest and appTestRequest['error'] == 'invalid_auth':
                flash("Slack App token not valid, " + str(appTestRequest['error']), 'danger')

            elif 'error' in appTestRequest and appTestRequest['error'] == 'missing_scope':
                flash("You are missing the connections:write scope for this token", 'danger')

        except:
            current_user.slackAppTokenValidity = "Invalid"
            flash("Requests had an issue with the site", 'danger')

        db.session.commit()

        # redirect the user to the previous page they visited
        if request.referrer is not None:
            return redirect(request.referrer)
        # if no referrer is found then use the form stored redirect
        return redirect(request.form['hiddenRedirect'])

    flash("Unauthorised access", 'danger')
    return redirect(url_for("Home"))


@app.route('/integrationSetup/validate/slackBotToken', methods=['GET', 'POST'])
def ValidateSlackBotToken():
    if current_user.is_authenticated:
        if request.method == "POST":
            validityCheck = "Invalid"
            try:
                authTestRequest = post("https://slack.com/api/auth.test", headers=slackHeader(current_user.slackToken))
                getScopesRequest = authTestRequest.headers
                authTestRequest = authTestRequest.json()

                if 'ok' in authTestRequest and authTestRequest['ok']:
                    validityCheck = "Incomplete"
                else:
                    flash("Slack Bot token not valid, " + str(authTestRequest['error']), 'danger')

                if 'x-oauth-scopes' in getScopesRequest and len(getScopesRequest['x-oauth-scopes'].split(',')) > 0:
                    # check that the list of scopes the bot has, matches the scopes required by the integration
                    scopesList = ['channels:history', 'channels:join', 'channels:manage', 'chat:write', 'chat:write.customize', 'chat:write.public', 'emoji:read', 'files:write', 'groups:read', 'groups:write', 'team:read', 'users.profile:read', 'users:read', 'users:read.email', 'users:write', 'channels:read']
                    missingScopes = list(filter(lambda scope: scope not in getScopesRequest['x-oauth-scopes'].split(','), scopesList))

                    if 'ok' in authTestRequest and authTestRequest['ok'] and not missingScopes:
                        validityCheck = "Valid"
                    elif missingScopes:
                        validityCheck = "Incomplete"
                        flash("Please add the following Slack Bot Scopes " + str(missingScopes), 'danger')

            except:
                validityCheck = "Invalid"
                flash("Requests had an issue with the site", 'danger')

            current_user.slackTokenValidity = validityCheck
            db.session.commit()

            if request.referrer is not None:
                return redirect(request.referrer)
            return redirect(request.form['hiddenRedirect'])


    flash("Unauthorised access", 'danger')
    return redirect(url_for("Home"))


@app.route('/integrationSetup/validate/slackUserToken', methods=['GET', 'POST'])
def ValidateSlackUserToken():
    if request.method == "POST":
        validityCheck = "Invalid"
        partial = [0,0]
        try:
            authTestRequest = post("https://slack.com/api/auth.test", headers=slackHeader(current_user.slackUserToken))
            getScopesRequest = authTestRequest.headers
            authTestRequest = authTestRequest.json()

            if 'ok' in authTestRequest and authTestRequest['ok']:
                validityCheck = "Incomplete"

                if 'x-oauth-scopes' in getScopesRequest and len(getScopesRequest['x-oauth-scopes'].split(',')) > 0:
                    # check that the list of scopes the user has, matches the scopes required by the integration
                    scopesList = ['admin', 'identify', 'channels:history', 'channels:read', 'emoji:read', 'team:read', 'users:read', 'users:read.email', 'channels:write', 'chat:write', 'groups:write', 'im:write', 'mpim:write']
                    missingScopes = list(filter(lambda scope: scope not in getScopesRequest['x-oauth-scopes'].split(','), scopesList))

                    if missingScopes:
                        flash("Please add the following Slack User Scopes " + str(missingScopes), 'danger')
                    else:
                        partial[0] = 1

                userInfoRequest = get(f"https://slack.com/api/users.info?user={authTestRequest['user_id']}", headers=slackHeader(current_user.slackToken))
                userInfoRequest = userInfoRequest.json()

                if 'ok' in userInfoRequest and userInfoRequest['ok']:
                    # if the user is not an admin
                    if 'user' in userInfoRequest and 'is_admin' in userInfoRequest['user']:
                        if userInfoRequest['user']['is_admin']:
                            partial[1] = 1
                        else:
                            validityCheck = "Incomplete"
                            flash("This user token does not have admin privileges", 'danger')
            else:
                flash("Slack User token not valid, " + str(authTestRequest['error']), 'danger')

        except:
            validityCheck = "Invalid"
            flash("Requests had an issue with the site", 'danger')
        
        # ensure both scope check and is_admin checks passed
        if sum(partial) == 2:
            validityCheck = "Valid"

        current_user.slackUserTokenValidity = validityCheck
        db.session.commit()

        if request.referrer is not None:
            return redirect(request.referrer)
        return redirect(request.form['hiddenRedirect'])

    flash("Unauthorised access you need to login first!", 'warning')
    return redirect(url_for('Home'))


@app.route('/integrationSetup/validate/zulipAdminRC', methods=['GET', 'POST'])
def ValidateZulipAdminRC():
    if request.method == "POST":
        validityCheck = "Invalid"
        zulipAuth = parseZulipRC(current_user.zulipAdminRC)
        try:
            sentFile = get(zulipAuth['site'] + "/api/v1/users/me", auth=(zulipAuth['email'], zulipAuth['key']))
            sentFile = sentFile.json()
            if 'result' in sentFile and sentFile['result'] == 'success':
                validityCheck = "Valid"
            else:
                flash("Requests had an issue with the site", 'danger')
        except:
            flash(".zulipAdminRC not valid", 'danger')

        current_user.zulipAdminRCValidity = validityCheck

        db.session.commit()

        if request.referrer is not None:
            return redirect(request.referrer)
        return redirect(request.form['hiddenRedirect'])

    flash("Unauthorised access you need to login first!", 'warning')
    return redirect(url_for('Home'))


@app.route('/integrationSetup/validate/zulipBotRC', methods=['GET', 'POST'])
def ValidateZulipBotRC():
    if request.method == "POST":
        validityCheck = "Invalid"
        zulipAuth = parseZulipRC(current_user.zulipBotRC)

        try:
            sentFile = get(zulipAuth['site'] + "/api/v1/users/me", auth=(zulipAuth['email'], zulipAuth['key']))
            sentFile = sentFile.json()
            if 'result' in sentFile and sentFile['result'] == 'success':
                validityCheck = "Valid"
            else:
                flash("Requests had an issue with the site", 'danger')
        except:
            flash(".zulipBotRC not valid", 'danger')

        current_user.zulipBotRCValidity = validityCheck
        db.session.commit()

        if request.referrer is not None:
            return redirect(request.referrer)
        return redirect(request.form['hiddenRedirect'])

    flash("Unauthorised access you need to login first!", 'warning')
    return redirect(url_for('Home'))


@app.route('/integrationSetup', methods=['GET', 'POST'])
def IntegrationSetup():
    if current_user.is_authenticated:
        return render_template('integrationSetup.html')

    flash("Unauthorised access you need to login first!", 'warning')
    return redirect(url_for('Home'))


@app.route('/integrationSetup/zulipBotRC', methods=['GET', 'POST'])
def ZulipBotRC():
    if current_user.is_authenticated:
        zulipRCForm = UploadForm()

        if zulipRCForm.validate_on_submit():
            f = request.files['file']

            if current_user is None:
                flash("Something went wrong with the database try logging in again", "danger")
                return render_template(url_for('Login'))

            # update the database with newest zulipBotRC
            f = f.read().decode()

            # sanitise the input to ensure it is not escaped when using JavaScript
            f = f.replace('\n', r' ').replace('\r', r' ').replace('  ', ' ')

            current_user.zulipBotRC = f
            current_user.zulipBotRCValidity = "Not Checked"
            db.session.commit()

            flash(".zulipBotRC file submitted successfully", 'success')

            return redirect(zulipRCForm.hiddenRedirect.data)

        return render_template('uploadFileTemplate.html', form=zulipRCForm, title='.ZulipBotRC upload', headingTitle='.zulipBotRC', labelTitle='Zulip Bot RC', fileUpload=True)

    flash("Unauthorised access you need to login first!", 'warning')
    return redirect(url_for('Home'))


@app.route('/integrationSetup/zulipAdminRC', methods=['GET', 'POST'])
def ZulipAdminRC():
    if current_user.is_authenticated:
        zulipRCForm = UploadForm()

        # if the zulip file was parsed through successfully
        if zulipRCForm.validate_on_submit():
            f = request.files['file']
            # if user is not found then take them to login
            if current_user is None:
                flash("Something went wrong with the database try logging in again", "danger")
                return render_template(url_for('Login'))

            # update the database with newest zulipBotRC
            f = f.read().decode()

            # sanitise the input to ensure it is not escaped when using JavaScript
            f = f.replace('\n', r' ').replace('\r', r' ').replace('  ', ' ')

            current_user.zulipAdminRC = f
            current_user.zulipAdminRCValidity = "Not Checked"
            db.session.commit()

            flash(".zulipAdminRC file submitted successfully", 'success')

            return redirect(zulipRCForm.hiddenRedirect.data)

        return render_template('uploadFileTemplate.html', form=zulipRCForm, title='.ZulipRC upload', headingTitle='.zulipAdminRC', labelTitle='Zulip Admin RC', fileUpload=True)

    flash("Unauthorised access you need to login first!", 'warning')
    return redirect(url_for('Home'))


@app.route('/integrationSetup/slackAppToken', methods=['GET', 'POST'])
def SlackAppToken():
    if current_user.is_authenticated:
        slackAppTokenForm = UploadForm()
        # if slack token form was submitted successfully
        if slackAppTokenForm.validate_on_submit():
            # if user is not found then take them to login
            if current_user is None:
                flash("Something went wrong with the database try logging in again", "danger")
                return render_template(url_for('Login'))

            # Add new slackToken to the database
            current_user.slackAppToken = slackAppTokenForm.file.data
            current_user.slackAppTokenValidity = "Not Checked"
            db.session.commit()

            flash("Slack App token submitted successfully", 'success')
            return redirect(slackAppTokenForm.hiddenRedirect.data)

        return render_template('uploadFileTemplate.html', form=slackAppTokenForm, title='Slack App Token Upload', headingTitle='Slack App Token', labelTitle='Slack App Token')

    flash("Unauthorised access you need to login first!", 'warning')
    return redirect(url_for('Home'))


@app.route('/integrationSetup/slackBotToken', methods=['GET', 'POST'])
def SlackToken():
    if current_user.is_authenticated:
        slackTokenForm = UploadForm()
        # if slack token form was submitted successfully
        if slackTokenForm.validate_on_submit():
            # if user is not found then take them to login
            if current_user is None:
                flash("Something went wrong with the database try logging in again", "danger")
                return render_template(url_for('Login'))

            # Add new slackToken to the database
            current_user.slackToken = slackTokenForm.file.data
            current_user.slackTokenValidity = "Not Checked"
            db.session.commit()

            flash("Slack Bot token submitted successfully", 'success')
            return redirect(slackTokenForm.hiddenRedirect.data)
        return render_template('uploadFileTemplate.html', form=slackTokenForm, title='Slack Bot Token Upload', headingTitle='Slack Bot Token', labelTitle='Slack Bot Token')

    flash("Unauthorised access you need to login first!", 'warning')
    return redirect(url_for('Home'))


@app.route('/integrationSetup/slackUserToken', methods=['GET', 'POST'])
def SlackUserToken():
    if current_user.is_authenticated:
        slackUserTokenForm = UploadForm()
        # if slack token form was submitted successfully
        if slackUserTokenForm.validate_on_submit():
            # if user is not found then take them to login
            if current_user is None:
                flash("Something went wrong with the database try logging in again", "danger")
                return render_template(url_for('Login'))

            # Add new slackToken to the database
            current_user.slackUserToken = slackUserTokenForm.file.data
            current_user.slackUserTokenValidity = "Not Checked"
            db.session.commit()

            flash("Slack User token submitted successfully", 'success')

            return redirect(slackUserTokenForm.hiddenRedirect.data)

        return render_template('uploadFileTemplate.html', form=slackUserTokenForm, title='Slack User Token Upload', headingTitle='Slack User Token', labelTitle='Slack User Token')

    flash("Unauthorised access you need to login first!", 'warning')
    return redirect(url_for('Home'))


@app.route('/logout')
def Logout():
    # call the login_manager, logout function to remove the current_user context
    logout_user()
    flash("You have logged out successfully!", 'success')

    # delete the session data for the user
    session.pop('slackPrefix', None)
    session.pop('zulipPrefix', None)
    session.pop('slackHistory', None)

    return redirect(url_for('Home'))


@app.route('/integrationSetup/newUploadFile', methods=['GET', 'POST'])
def NewUploadFile():
    if current_user.is_authenticated:
        newUploadFile = UploadForm()
        if newUploadFile.validate_on_submit():
            current_user.newUploadFile = newUploadFile.file.data
            current_user.newUploadFile = "Not Checked"
            db.session.commit()

            flash("Slack App token submitted successfully", 'success')
            return redirect(newUploadFile.hiddenRedirect.data)

        return render_template('uploadFileTemplate.html', form=newUploadFile, title='Slack App Token Upload', headingTitle='Slack App Token', labelTitle='Slack App Token')

    flash("Unauthorised access you need to login first!", 'warning')
    return redirect(url_for('Home'))
