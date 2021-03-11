from flaskFiles import db
from flask_login import UserMixin

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