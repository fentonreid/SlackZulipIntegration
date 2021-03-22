from json import dumps
from flask import session
from flask_login import current_user
from requests import get, post
from integration.markdown.toZulip import zulipMarkdown
from integration.webhooks.slackWebHook import renameChannel, channelNameToID, slackWebhook
from integration.webhooks.zulipWebHook import zulipWebhook, deleteTopic, renameTopic, getZulipTopicList
from urllib import parse
from integration.utilities import slackHeader, parseZulipRC


def channelIDToName(channelID):
    """
    Given a channel ID find the channel name for that ID.

    :param channelID: ID of the channel you would like the name for
    :type channelID: String
    """
    # channel list request
    channelListRequest = get("https://slack.com/api/conversations.list?" + parse.urlencode({"exclude_archived": True, "limit": 1000}),headers=slackHeader(current_user.slackToken))
    channelListRequest = channelListRequest.json()
    return next((current['name'] for current in channelListRequest['channels'] if current['id'] == channelID), None)


def handleFiles(files):
    """
    Converts a json object into a list of tuples with filename and fileurl that can be processed further.

    :param files: A json object that contains the name, url download of the file, plus other unused information
    :type: JSON
    """
    return [(file['name'], file['url_private']) for file in files]


def updateHistory(events):
    """
    Maintains a reference of the Slack channels prior to the current event, used for determining the channel that was deleted
    
    :param events: JSON message containing event information
    :type events: JSON payload
    """
    if events['type'] != 'channel_deleted':
        # get all the channels in Slack
        channelListRequest = get("https://slack.com/api/users.conversations?" + parse.urlencode({"exclude_archived": True, "limit": 1000}),  headers=slackHeader(current_user.slackToken)).json()
        channelDict = {}
        for channel in channelListRequest['channels']:
            channelDict[channel['id']] = channel['name']

        session['slackChannels'] = channelDict


def checkSlackStreamExists():
    """
    Ensure the Slack Stream is Zulip exists before processing events
    """
    zulipAuth = parseZulipRC(current_user.zulipBotRC)
    streamIDRequest = get(zulipAuth['site'] + "/api/v1/get_stream_id?" + parse.urlencode({'stream': 'Slack'}), auth=(zulipAuth['email'], zulipAuth['key'])).json()
    if 'stream_id' in streamIDRequest:
        return True
    else:
        return False


def slackEvents(events):
    """
    All Slack events are sent here, this function handles multiple events.

    :param events: JSON message containing information on the Slack event
    :type events: JSON payload
    """
    slackAuth = slackHeader(current_user.slackToken)
    zulipAuth = parseZulipRC(current_user.zulipBotRC)
    updateHistory(events)

    # if the Slack stream does not exist
    if checkSlackStreamExists() is False:
        # create the Slack stream
        userList = []
        membersRequest = get(f"https://slack.com/api/conversations.members?{parse.urlencode({'channel': channelNameToID('general')})}", headers=slackAuth).json()

        if 'ok' in membersRequest and 'members' in membersRequest:
            members = membersRequest['members']
            for memberID in members:
                userRequest = get(f"https://slack.com/api/users.profile.get?{parse.urlencode({'user': memberID})}", headers=slackAuth).json()
                if 'ok' in userRequest and 'profile' in userRequest and 'email' in userRequest['profile']:  userList.append(userRequest['profile']['email'])
        
        # add the IntegrationBot to Zulip Slack Stream
        userList.append(zulipAuth['email'])
        post(zulipAuth['site'] + "/api/v1/users/me/subscriptions", auth=(zulipAuth['email'], zulipAuth['key']), data={'subscriptions': '[{"name": "Slack"}]', 'principals': dumps(userList)})

    if 'user' in events:
        # check if the user who initiated the event is the bot
        checkBotRequest = get("https://slack.com/api/auth.test", headers=slackAuth).json()
        # if the user is the integration bot then stop processing
        if 'subtype' in events and events['subtype'] == 'channel_join':
            pass
        elif events['user'] == checkBotRequest['user_id']:
            return None


    # if the Slack event is a message
    if events['type'] == 'message':
        # message holds sub-types, checking for added users and when a channel rename occurs
        if 'subtype' in events:
            if events['subtype'] == 'channel_join':
                # check if the user who initiated the event is the bot
                checkBotRequest = get("https://slack.com/api/auth.test", headers=slackAuth).json()

                if events['user'] == checkBotRequest['user_id']:
                    # if slack created a channel then send the message to Zulip, ignore otherwise
                    slackGetName = channelIDToName(events['channel'])

                    # if the topic does not already exist in Zulip then create it
                    if slackGetName not in getZulipTopicList():
                        return zulipWebhook(slackGetName, "Slack created this channel")
                else:
                    return None
            
            elif events['subtype'] == 'message_changed':
                return None

            elif events['subtype'] == 'channel_name':
                # to make sure the user doesn't change the name of the general channel
                if events['old_name'] != 'general':
                    renameTopic(events['old_name'], events['name'])
                else:
                    renameChannel(events['name'], events['old_name'])
                    slackWebhook(channelNameToID("general"), "You cannot rename the general chat!")
                return "slack renamed a channel"

        # convert message to slack markdown before being sent
        slackMessage = zulipMarkdown(events['text'])

        # if files are present in the Slack message event
        if 'files' in events:
            slackMessage = slackMessage[0], handleFiles(events['files'])

        # get channel name from id
        channelID = events['channel']
        channelName = "general"

        channelListRequest = get("https://slack.com/api/conversations.list?" + parse.urlencode({"exclude_archived" : True, "limit" : 1000}), headers=slackAuth)
        channelListRequest = channelListRequest.json()

        # if the request was successful
        if 'ok' in channelListRequest and channelListRequest['ok']:
            channelName = next((current['name'] for current in channelListRequest['channels'] if current['id'] == channelID), "general")

        # need to get username of the sender rather than just the user_id
        userNameRequest = get(f"https://slack.com/api/users.info?{parse.urlencode({'user': events['user']})}", headers=slackAuth)
        userNameRequest = userNameRequest.json()

        if 'ok' in userNameRequest and userNameRequest['ok'] and 'user' in events:
            # preparation for the sending of the message to Zulip
            customMessage = slackCustomPrefix(userNameRequest['user'], channelName)
            return zulipWebhook(channelName, f"{customMessage} {slackMessage[0]}", files=slackMessage[1])


    # if a channel created event is detected
    elif events['type'] == 'channel_created':
        return None

    # if a channel deleted event is detected
    elif events['type'] == 'channel_deleted':
        # delete the channel using the old channel list as reference
        if session.get('slackChannels') is not None:
            deleteTopic(session['slackChannels'][events['channel']])
            session['slackChannels'].pop(events['channel'], None)
            return "Slack deleted a channel"
        # if the integration was started and the slackChannel session does not exist
        else:
            slackWebhook("general", "Could not tell what channel was deleted")

    else:
        return "Slack can't handle this event"

    return None


def slackCustomPrefix(userNameRequest, channelName, **kwargs):
    """
    Replace the variable short-codes with the data found in the event.

    :param userNameRequest: userNameRequest JSON object, contains the username of the user who initiated the event
    :type userNameRequest: JSON Payload

    :param channelName: name of the channel the event occurred in
    :type channelName: String
    """
    # parse the original
    userEmail = ""
    if 'profile' in userNameRequest and 'email' in userNameRequest['profile']:
        userEmail = userNameRequest['profile']['email']

    # for unit test purposes
    if kwargs.get('testing', None) is not None:
        return kwargs.get('testing').replace('{name}', userNameRequest['real_name']).replace('{email}', userEmail).replace('{channel}', channelName)

    return session['zulipPrefix'].replace('{name}', userNameRequest['real_name']).replace('{email}', userEmail).replace('{channel}', channelName)