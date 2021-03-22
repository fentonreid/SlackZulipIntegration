from urllib import parse
from flask_login import current_user
from integration.utilities import parseZulipRC, slackHeader
from requests import get, post
from datetime import datetime


def channelNameToID(channelName):
    """
    Converts a Slack channel name to its corresponding channel ID value.

    :param channelName: The channel name to be converted
    :type channelName: String
    """
    slackAuth = slackHeader(current_user.slackToken)

    # channel list request
    channelListRequest = get("https://slack.com/api/conversations.list?" + parse.urlencode({"exclude_archived": True, "limit": 1000}), headers=slackAuth)
    channelListRequest = channelListRequest.json()

    # get a list of all the channel names and id's
    return next((current['id'] for current in channelListRequest['channels'] if current['name'] == channelName), None)


def slackWebhook(channel, content, **kwargs):
    """
    Post a message to a Slack channel.

    :param channel: Channel to send message to
    :type channel: String

    :param content: A Slack formatted message
    :type content: String

    :param kwargs: Files
    :type kwargs: List of Tuples that for each element contain a filename and URL
    """

    zulipAuth = parseZulipRC(current_user.zulipBotRC)
    slackAuth = slackHeader(current_user.slackToken)

    # create the channel if it does not exist in the slack workplace
    createChannelRequest = get(f"https://slack.com/api/conversations.create?{parse.urlencode({'name' : channel})}", headers=slackAuth).json()

    # if the channel was created successfully
    if createChannelRequest['ok']:
        if 'channel' in createChannelRequest:
            # get a list of all members in the general channel
            targetID = channelNameToID("general")
            channelMembersRequest = get(f"https://slack.com/api/conversations.members?{parse.urlencode({'channel': targetID})}", headers=slackAuth).json()

            # add all members of the slack workplace into to the newly created channel
            userIDList = []
            if 'members' in channelMembersRequest:
                userIDList = channelMembersRequest['members']

            # add users to the channel
            params = {
                "channel": channelNameToID(channel),
                "users": userIDList
            }

            # add all members to the new channel
            inviteUsersRequest = post(f"https://slack.com/api/conversations.invite?{parse.urlencode(params)}", headers=slackAuth, json=params).json()

            # the userIDList contains the user that created the channel therefore if a specific error with the inviteUsersRequest occurred try again
            if 'error' in inviteUsersRequest and inviteUsersRequest['error'] == 'cant_invite_self':
                # remove all users already added to the channel
                [userIDList.remove(conflictedUser['user']) for conflictedUser in inviteUsersRequest['errors'] if conflictedUser['user'] in userIDList]

                # try the invite again
                inviteUsersRequest = post(f"https://slack.com/api/conversations.invite?{parse.urlencode(params)}", headers=slackAuth, json=params).json()
                if 'error' in inviteUsersRequest:
                    return "Issue with inviting"

    # post the message content to the specific Slack channel
    get(f"https://slack.com/api/chat.postMessage?{parse.urlencode({'channel' : channel, 'text': content})}", headers=slackAuth).json()

    # get the files parameter, if non specified then default to empty list
    if kwargs.get('files') is not None:
        for filename, fileurl in kwargs.get('files'):
            sentFile = get(fileurl, auth=(zulipAuth['email'], zulipAuth['key']))

            # post file to the same channel
            post(f"https://slack.com/api/files.upload?{parse.urlencode({'channels': channel, 'filename': filename})}", headers=slackAuth, files={"file": sentFile.content})

    return "Message sent"


def renameChannel(oldChannelName, newChannelName):
    """
    Renames a channel.

    :param oldChannelName: The old channel name being renamed
    :type oldChannelName: String

    :param newChannelName: The new name the channel should take on
    :type newChannelName: String
    """

    # rename channel in slack
    message = {
        "channel": channelNameToID(oldChannelName),
        "name": newChannelName
    }


    renameRequest = post("https://slack.com/api/conversations.rename", headers=slackHeader(current_user.slackUserToken), json=message)
    if renameRequest.status_code == 200:
        return "Zulip renamed a Slack channel"


def deleteChannel(channelName):
    """
    Delete a channel functionality is not apart of the Slack api, therefore the channel that requires *deleting* is instead given a randomly generated name of max length 60 and archived.

    :param channelName: Name of the Slack channel to delete
    :type channelName: String
    """
    renameTo = ''.join([char if char.isnumeric() else '_' for char in str(datetime.utcnow())])
    renameChannel(channelName, renameTo)

    post(f"https://slack.com/api/conversations.archive?{parse.urlencode({'channel' : channelNameToID(renameTo)})}", headers=slackHeader(current_user.slackUserToken))
    return "Zulip deleted a Slack channel"