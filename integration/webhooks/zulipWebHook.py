from flask_login import current_user
from integration.utilities import slackHeader, parseZulipRC
from requests import post, get, patch


def zulipWebhook(topic, content, **kwargs):
    """
    Post a message to Zulip.

    :param topic: Topic to send the message to
    :type topic: String

    :param content: A Zulip formatted string
    :type content: String

    :param kwargs: Files
    :type kwargs: List of Tuples that contains a filename and URL
    """

    zulipAuth = parseZulipRC(current_user.zulipBotRC)
    slackAuth = slackHeader(current_user.slackToken)

    message = {
        "type": "stream",
        "to": "Slack",
        "topic": topic,
        "content": content
    }

    files = kwargs.get('files')
    if files is not None:
        for (filename, fileurl) in files:
            # Get the raw content of the uploaded Slack file, by providing authentication to private URL
            fileFromSlack = get(fileurl, headers=slackAuth)
            # ensure file is under the 25MB Zulip limit
            if int(fileFromSlack.headers['content-Length']) < 25_000_000:
                result = post(zulipAuth['site'] + '/api/v1/user_uploads', files={'filename': (filename, fileFromSlack.content)}, auth=(zulipAuth['email'], zulipAuth['key']))
                message['content'] += f"[{filename}]({result.json()['uri']})" + "\n"
            else:
                message['content'] += f"File too large to display directly [{filename}]({fileurl})" + "\n"

    # post the message to Zulip
    post(zulipAuth['site'] + "/api/v1/messages", auth=(zulipAuth['email'], zulipAuth['key']), data=message)

    return "Message sent"


def getZulipTopicList():
    """
    Get a list of topics in the Zulip workspace.
    """
    zulipAuth = parseZulipRC(current_user.zulipBotRC)

    getAllTopicsRequest = get(zulipAuth['site'] + f"/api/v1/users/me/{getStreamID()}/topics", auth=(zulipAuth['email'], zulipAuth['key']))
    getAllTopicsRequest = getAllTopicsRequest.json()['topics']

    return [topic['name'] for topic in getAllTopicsRequest]


def getStreamID(streamName='Slack'):
    """
    By default get the StreamID of the Slack stream in Zulip.

    :param streamName: The stream name to find the ID of, by default 'Slack'
    :type streamName: String
    """
    zulipAdminAuth = parseZulipRC(current_user.zulipAdminRC)
    return get(zulipAdminAuth['site'] + "/api/v1/get_stream_id", auth=(zulipAdminAuth['email'], zulipAdminAuth['key']), params={'stream' : streamName}).json()['stream_id']


def deleteTopic(topicName):
    """
    Given a topic name delete it from Zulip if it exists

    :param topicName: Name of topic to delete
    :type topicName: String
    """
    zulipAdminAuth = parseZulipRC(current_user.zulipAdminRC)

    # Delete method from api, not currently added to documentation but live: https://github.com/zulip/zulip/commit/ac55a5222c977ae2c507fb34ec5081c6ab018c16
    post(zulipAdminAuth['site'] + "/json/streams/" + str(getStreamID()) + "/delete_topic", data={"topic_name": topicName}, auth=(zulipAdminAuth['email'], zulipAdminAuth['key']))


def renameTopic(oldName, newName):
    """
    Rename a topic in the Zulip workplace.

    :param oldName: The old channel name
    :type oldName: String

    :param newName: The new channel name
    :type newName: String

    """
    zulipAuth = parseZulipRC(current_user.zulipBotRC)

    params = {'anchor': 'newest',
              'num_before': 1,
              'num_after': 0,
              'narrow': '[{"operator": "stream", "operand" : "Slack"}, {"operator" : "topic", "operand" : "' + oldName + '"}]'
              }

    messageID = get(zulipAuth['site'] + "/api/v1/messages", auth=(zulipAuth['email'], zulipAuth['key']), params=params)
    messageID = messageID.json()
    try:
        messageID = messageID['messages'][0]['id']
    except:
        messageID = None

    if messageID is not None:
        message = {
            'topic': newName,
            'propagate_mode': 'change_all'
        }

        # change all the messages to have a new topic
        patch(zulipAuth['site'] + "/api/v1/messages/" + str(messageID), auth=(zulipAuth['email'], zulipAuth['key']), data=message)