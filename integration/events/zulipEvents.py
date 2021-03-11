import re
from flask import session
from requests import get, post
from flask_login import current_user
from integration.startup.utilities import parseZulipRC
from integration.markdown.toSlack import slackMarkdown
from integration.webhooks.slackWebHook import slackWebhook, renameChannel, deleteChannel
from integration.webhooks.zulipWebHook import getZulipTopicList, getStreamID, renameTopic


def zulipEvents(events):
    """
    All Zulip events are sent here, this function handles multiple events.

    :param events: JSON message containing information on the Zulip event
    :type events: JSON payload
    """
    print(events)
    zulipAuth = parseZulipRC(current_user.zulipBotRC)

    # if the event is a message
    if events[0]['type'] == 'message':
        # if the event wasn't sent by the integration bot
        if events[0]['message']['sender_email'] != zulipAuth['email']:
            # convert message to slack markdown before being sent
            if slackNamingValidation(events[0]['message']['subject']) and len(events[0]['message']['subject']) <= 80:
                zulipMessage = slackMarkdown(events[0]['message']['content'])
                customMessage = zulipCustomPrefix(events[0])
                return slackWebhook(events[0]['message']['subject'], f"{customMessage} {zulipMessage[0]}", files=zulipMessage[1])
            else: # the Zulip topic is named incorrectly
                formatTopicName(events)

            return "Not a valid Slack topic"

    # the event is topic renaming
    elif events[0]['type'] == 'update_message' and 'orig_subject' in events[0] and 'subject' in events[0]:
        if slackNamingValidation(events[0]['subject']) and len(events[0]['subject']) <= 80:
            return renameChannel(events[0]['orig_subject'], events[0]['subject'])
        else:
            # format to Slack valid form
            channelName = events[0]['subject'].lower().replace(' ', '')
            if len(channelName) > 80:
                channelName = channelName[:80]

            newChannelName = ""
            for char in channelName:
                if char.isalnum() or char in ['_', '-']:
                    newChannelName += char

            zulipTopicList = getZulipTopicList()
            counter = 0
            tempChannelName = newChannelName
            while newChannelName in zulipTopicList:
                if len(newChannelName + str(counter)) < 80:
                    newChannelName = tempChannelName + str(counter)
                else:
                    newChannelName = tempChannelName[:(80 - len(str(counter)))] + str(counter)
                counter += 1

            # rename the invalid Zulip topic
            renameTopic(events[0]['subject'], newChannelName)
            return renameChannel(events[0]['orig_subject'], newChannelName)

    # if the event is a delete message
    elif events[0]['type'] == "delete_message":
        # check if the topic still exists
        if topicDeleted(events[0]['topic'], events[0]['stream_id']):
            return deleteChannel(events[0]['topic'])

    else:
        return "Zulip can't handle this event"


def topicDeleted(topicName, streamID):
    """
    Given a Zulip topic, delete it from Zulip

    :param topicName: Name of the topic to delete
    :type topicName: String

    :param streamID: `Slack` Stream ID in Zulip
    :type streamID: Integer
    """
    zulipAuth = parseZulipRC(current_user.zulipBotRC)

    getTopicsRequest = get(zulipAuth['site'] + f"/api/v1/users/me/{streamID}/topics", auth=(zulipAuth['email'], zulipAuth['key']))
    getTopicsRequest = getTopicsRequest.json()

    return list(filter(lambda topic: topic['name'] == topicName, getTopicsRequest['topics'])) == []


def slackNamingValidation(channelName):
    """
    Ensure the given topic name is Slack valid, this means a length of 1 and less than 80 and no special characters or punctuation.

    :param channelName: The name of the Slack Channel
    :type: channelName: String

    :param kwargs:
    :type:
    """
    # Channel names can only contain lowercase letters, numbers, hyphens, and underscores, and must be 80 characters or less.
    slackName = re.compile(r'^([a-z0-9]+[_\-]*|[_\-]*[a-z0-9]+)([a-z0-9]*[_\-]*)*$')

    return slackName.match(channelName) is not None


def formatTopicName(events):
    """
    Given an invalid Zulip channel name change it to be Slack safe

    :param channelName: Name of the invalid topic to change for Slack
    :type: channelName: String
    """
    # format to Slack valid form
    channelName = events[0]['message']['subject'].lower().replace(' ', '')
    if len(channelName) > 80:
        channelName = channelName[:80]

    newChannelName = ""
    for char in channelName:
        if char.isalnum() or char in ['_', '-']:
            newChannelName += char

    zulipTopicList = getZulipTopicList()
    counter = 0
    tempChannelName = newChannelName
    while newChannelName in zulipTopicList:
        if len(newChannelName+str(counter)) < 80:
            newChannelName = tempChannelName + str(counter)
        else:
            newChannelName = tempChannelName[:(80-len(str(counter)))] + str(counter)
        counter += 1

    # delete the invalid Topic
    zulipAdminAuth = parseZulipRC(current_user.zulipAdminRC)
    post(zulipAdminAuth['site'] + "/json/streams/" + str(getStreamID()) + "/delete_topic", data={"topic_name": events[0]['message']['subject']}, auth=(zulipAdminAuth['email'], zulipAdminAuth['key']))
    return slackWebhook(newChannelName, f"{zulipCustomPrefix(events[0])} Zulip Topic renamed to be Slack safe")


def zulipCustomPrefix(events, **kwargs):
    """
    Replace the variable short-codes with the data found in the event.

    :param events: JSON message containing information on the Zulip event
    :type events: JSON payload
    """

    if kwargs.get('testing', None) is not None:
        return kwargs.get('testing').replace('{name}', events['message']['sender_full_name']).replace('{email}', events['message'][ 'sender_email']).replace('{channel}', events['message']['subject'])

    # parse the original
    return session['slackPrefix'].replace('{name}', events['message']['sender_full_name']).replace('{email}', events['message']['sender_email']).replace('{channel}', events['message']['subject'])