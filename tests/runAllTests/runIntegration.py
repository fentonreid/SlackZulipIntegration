import os
from flaskFiles import app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user
from dotenv import load_dotenv
from pytest import main

app.testing = True
app.secret_key = os.urandom(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///..//tests//testDatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_ENABLED'] = False
login_manager = LoginManager()
login_manager.init_app(app)
db = SQLAlchemy(app)
load_dotenv(dotenv_path="../.env")

# if the testDatabase exists then delete in preparation for testing
if os.path.exists(os.getcwd() + r'..\testDatabase.db'):
    os.remove(os.getcwd() + r'..\testDatabase.db')


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


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


def callMarkdownTests():
    with app.test_client() as test_client:
        with app.app_context():
            # Signup and Login the user
            test_client.post('/signup', data={'username': 'test', 'password': 'test', 'confirmPassword': 'test'}, follow_redirects=True)
            test_client.post('/login', data={'username': 'test', 'password': 'test'}, follow_redirects=True)

            # Add the current_user details based on .env files
            current_user.slackAppToken = os.environ.get("slackAppToken")
            current_user.slackToken = os.environ.get("slackToken")
            current_user.slackUserToken = os.environ.get("slackUserToken")
            current_user.zulipAdminRC = os.environ.get("zulipAdminRC").replace(r'\n', ' ')
            current_user.zulipBotRC = os.environ.get("zulipBotRC").replace(r'\n', ' ')

            db.session.commit()

            # Call PyTest
            os.chdir("..")
            main(["integration/", "-v", "-r a", "--tb=native"])


callMarkdownTests()