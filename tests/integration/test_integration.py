from json import dumps
from urllib import parse
from flask import session
from flask_login import current_user
from requests import get, post, head, delete
from integration.events.zulipEvents import zulipEvents, zulipCustomPrefix
from integration.webhooks.slackWebHook import deleteChannel
from integration.startup.utilities import parseZulipRC, slackHeader
from integration.events.slackEvents import slackEvents, slackCustomPrefix

zulipAuth = parseZulipRC(current_user.zulipBotRC)
slackAuth = slackHeader(current_user.slackToken)
zulipAdminAuth = parseZulipRC(current_user.zulipAdminRC)


def getSlackStreamID():
    zulipAuth = parseZulipRC(current_user.zulipBotRC)
    streamIDRequest = get(zulipAuth['site'] + "/api/v1/get_stream_id?" + parse.urlencode({'stream' : 'Slack'}), auth=(zulipAuth['email'], zulipAuth['key'])).json()

    if 'stream_id' in streamIDRequest:
        return streamIDRequest['stream_id']
    return None


def prepareSlack():
    """
    Move all channels excluding Slack to be archived

    """
    listChannelsRequest = get("https://slack.com/api/conversations.list?" + parse.urlencode({"exclude_archived" : True, "limit" : 1000}), headers=slackAuth)
    assert listChannelsRequest.status_code == 200, "Requests failed to fetch :: https://slack.com/api/conversations.list"

    [deleteChannel(channel['name']) for channel in  listChannelsRequest.json()['channels'] if channel['name'] != "general"]


def prepareZulip():
    """
    Delete Slack Stream in Zulip workspace
    """
    slackStream = getSlackStreamID()

    if slackStream is not None:
        delete(zulipAuth['site'] + f'/api/v1/streams/{slackStream}', auth=(zulipAdminAuth['email'], zulipAdminAuth['key']))


prepareSlack()
prepareZulip()

def getChannelID(channelName):
    slackAuth = slackHeader(current_user.slackToken)

    listChannelsRequest = get("https://slack.com/api/conversations.list?" + parse.urlencode({"exclude_archived" : True, "limit" : 1000}), headers=slackAuth)
    assert listChannelsRequest.status_code == 200, "Requests failed to fetch :: https://slack.com/api/conversations.list"
    listChannelsRequest = listChannelsRequest.json()
    return next((current['id'] for current in listChannelsRequest['channels'] if current['name'] == channelName), None)


def userEmailList():
    """
    Returns a list of emails for each member in the General Slack channel
    """
    slackAuth = slackHeader(current_user.slackToken)

    userList = []
    userID = None
    membersRequest = get(f"https://slack.com/api/conversations.members?{parse.urlencode({'channel' : getChannelID('general')})}", headers=slackAuth)
    assert membersRequest.status_code == 200, "Requests failed to fetch :: https://slack.com/api/conversations.members"

    membersRequest = membersRequest.json()
    if 'ok' in membersRequest and 'members' in membersRequest:
        members = membersRequest['members']
        for memberID in members:
            userRequest = get(f"https://slack.com/api/users.profile.get?{parse.urlencode({'user' : memberID})}", headers=slackAuth)
            assert userRequest.status_code == 200, "Requests failed to fetch :: https://slack.com/api/users.profile.get"

            userRequest = userRequest.json()
            if 'ok' in userRequest and 'profile' in userRequest and 'email' in userRequest['profile']:
                userList.append(userRequest['profile']['email'])
                if userID is None:
                    userID = memberID

        return userID, userList


def getBotID():
    slackAuth = slackHeader(current_user.slackToken)

    authTestRequest = post("https://slack.com/api/auth.test", headers=slackAuth, data={"exclude_archived": True})
    assert authTestRequest.status_code == 200, "Requests failed to fetch :: https://slack.com/api/auth.test"

    authTestRequest = authTestRequest.json()
    assert authTestRequest['ok'] and 'bot_id' in authTestRequest, "The Slack token provided failed to authenticate " + str(authTestRequest['error'])

    return authTestRequest['user_id']


integrationBotID = getBotID()
userID, userIDList = userEmailList()


def createSlackTestChannel():
    slackAuth = slackHeader(current_user.slackToken)

    createChannelRequest = post("https://slack.com/api/conversations.create", headers=slackAuth, data={"name": "test_channel"})
    assert createChannelRequest.status_code == 200, "Requests failed to fetch :: https://slack.com/api/conversations.create"
    createChannelRequest = createChannelRequest.json()

    assert createChannelRequest['ok'], "Failed to create channel, error :: " + str(createChannelRequest['error'])

    # add user to channel
    addUserRequest = post("https://slack.com/api/conversations.invite", headers=slackAuth, data={"channel": createChannelRequest['channel']['id'], "users" : userID})
    assert addUserRequest.status_code == 200

    return createChannelRequest['channel']['id']


class TestFirstTimeSetup:
    def test_slack_token(self):
        authTestRequest = post("https://slack.com/api/auth.test", headers=slackAuth, data={"exclude_archived": True})
        assert authTestRequest.status_code == 200, "Requests failed to fetch :: https://slack.com/api/auth.test"

        authTestRequest = authTestRequest.json()
        assert authTestRequest['ok'] and 'bot_id' in authTestRequest, "The Slack token provided failed to authenticate " + str(authTestRequest['error'])


    def test_zulipRC(self):
        authTestRequest = get(zulipAuth['site'] + "/api/v1/users/me", auth=(zulipAuth['email'], zulipAuth['key']))
        assert authTestRequest.status_code == 200, "Requests failed to fetch :: https://yourZulipDomain.zulipchat.com/api/v1/users/me"

        authTestRequest = authTestRequest.json()
        assert (authTestRequest['result'] == 'success' and authTestRequest['is_bot']), "The ZulipRC provided failed to authenticate " + str(authTestRequest['msg'])


    def test_bot_scopes(self):
        # this test checks to ensure that the bot has the required scopes to perform the integration
        getScopesRequest = head("https://slack.com/api/auth.test", headers=slackAuth)
        assert getScopesRequest.status_code == 200, "Requests failed to fetch :: https://slack.com/api/files.list"

        getScopesRequest = getScopesRequest.headers
        assert ('x-oauth-scopes' in getScopesRequest and len(getScopesRequest['x-oauth-scopes'].split(',')) > 0), "Failed to fetch oauth scopes from getScopesRequest"

        # check that the list of scopes the bot has, matches the scopes required by the integration
        scopesList = ['channels:history', 'channels:join', 'channels:manage', 'chat:write', 'chat:write.customize', 'chat:write.public', 'emoji:read', 'files:write', 'groups:read', 'groups:write', 'team:read', 'users.profile:read', 'users:read', 'users:read.email', 'users:write', 'channels:read']

        missingScopes = list(filter(lambda scope: scope not in getScopesRequest['x-oauth-scopes'].split(','), scopesList))
        assert len(missingScopes) == 0, "Slack Token needs the following oauth scopes :: " + str(missingScopes)


    def test_createStream(self):
        createSlackStreamRequest = post(zulipAuth['site'] + "/api/v1/users/me/subscriptions", auth=(zulipAuth['email'], zulipAuth['key']), data={'subscriptions': '[{"name": "Slack"}]', 'principals': dumps(list(set(userIDList)))})
        assert createSlackStreamRequest.status_code == 200, "Requests failed to fetch :: https://yourZulipDomain.zulipchat.com/api/v1/users/me/subscriptions"

        createSlackStreamRequest = createSlackStreamRequest.json()
        assert createSlackStreamRequest['result'] == 'success', "Zulip failed to respond"
        assert(len(createSlackStreamRequest['subscribed']) + len(createSlackStreamRequest['already_subscribed']) == len(userIDList)), "Zulip couldn't add all the members to the Slack Stream"


    def test_addBots(self):
        # add integration bot to Slack General Channel
        getSlackChannels = get("https://slack.com/api/conversations.list?" + parse.urlencode({"exclude_archived" : True, "limit" : 1000}), headers=slackAuth)
        assert getSlackChannels.status_code == 200, "Requests failed to fetch :: https://slack.com/api/conversations.list"

        getSlackChannels = getSlackChannels.json()
        assert getSlackChannels['ok'], "Slack conversations list errored with " + str(getSlackChannels['error'])

        channelID = [channel['id'] for channel in getSlackChannels['channels'] if channel['name'] == 'general']

        addBotToChannelRequest = post("https://slack.com/api/conversations.join", headers=slackAuth, data={'channel': channelID})
        assert addBotToChannelRequest.status_code == 200, "Requests failed to fetch :: https://slack.com/api/conversations.join"

        # add integration bot to Zulip Slack Stream
        zulipAddBotRequest = post(zulipAuth['site'] + "/api/v1/users/me/subscriptions", auth=(zulipAuth['email'], zulipAuth['key']), data={'subscriptions': '[{"name": "Slack"}]', 'principals': dumps([zulipAuth['email']])})
        assert zulipAddBotRequest.status_code == 200, "Requests failed to fetch :: https://yourZulipDomain.zulipchat.com/api/v1/users/me/subscriptions"

        zulipAddBotRequest = zulipAddBotRequest.json()

        # if it's a success or the bot is already added
        assert (zulipAddBotRequest['result'] == 'success' and (len(zulipAddBotRequest['already_subscribed']) == 1 or len(zulipAddBotRequest['subscribed']) == 1)), "Zulip failed to add bot to Slack stream"



class TestCreation:
    def test_creation_slack(self):
        # get the id of test_channel
        channelID = createSlackTestChannel()

        # check the bot is added correctly and Zulip WebHook returns a match
        createChannelEvent = slackEvents({'type': 'message', 'subtype': 'channel_join', 'user': integrationBotID, 'text': '', 'channel': channelID, 'channel_type': 'channel'})  # need to convert channel id to the created one
        assert createChannelEvent == "Message sent", "Zulip could not create channel "

        # check in Zulip
        params = {'anchor': 'newest',
                  'num_before': 1, 'num_after': 0,
                  'narrow': '[{"operator": "stream", "operand" : "Slack"}, {"operator": "topic", "operand" : "test_channel"}]',
                  'apply_markdown': 'false'
                  }

        lastMessage = get(zulipAuth['site'] + "/api/v1/messages", params=params, auth=(zulipAuth['email'], zulipAuth['key']))
        assert lastMessage.status_code == 200, "Failed to fetch :: https://yourZulipDomain.zulipchat.com/api/v1/messages"

        # check that the message is present in the test_channel stream and that it has a certain message type
        lastMessage = lastMessage.json()

        assert lastMessage['result'] == 'success' and 'messages' in lastMessage, "Failed to retrieve messages from Zulip " + str(lastMessage['msg'])
        assert lastMessage['messages'][0]['subject'] == 'test_channel' and lastMessage['messages'][0]['content'] == 'Slack created this channel'

        deleteChannel("test_channel")


    def test_creation_zulip(self):
        # Create a zulip event
        createTopicEvent = zulipEvents([{'type': 'message', 'message': {'content': 'testing', 'subject': 'test_channel', 'sender_full_name': 'FR acc 1', 'sender_email': 'fenton.reid.2017@uni.strath.ac.uk', 'sender_realm_str': 'fenton', 'display_recipient': 'Slack', 'type': 'stream'}}])
        assert createTopicEvent == "Message sent", "Slack could not create channel"

        # Checking Slack
        listChannelsRequest = get("https://slack.com/api/conversations.list?" + parse.urlencode({"exclude_archived" : True, "limit" : 1000}), headers=slackAuth)
        assert listChannelsRequest.status_code == 200, "Requests failed to fetch :: https://slack.com/api/conversations.list"

        listChannelsRequest = listChannelsRequest.json()
        assert listChannelsRequest['ok'], "Failed to list channels, error :: " + str(listChannelsRequest['error'])
        assert ('channels' in listChannelsRequest and len(listChannelsRequest['channels']) == 2), "general and test_channel not in the Slack workplace"


class TestMessageSending:
    def test_message_sending_slack(self):
        # send test message to Zulip via Slack events
        sendMessageJSON = {'type': 'message', 'user' : userID, 'text' : 'Test Message Event', 'channel' : getChannelID("test_channel")}
        sendMessageJSON = slackEvents(sendMessageJSON)
        assert sendMessageJSON == "Message sent", "Slack Events could not send this message"

        # check that the message was received in Zulip
        params = {'anchor': 'newest',
                  'num_before': 1, 'num_after': 0,
                  'narrow': '[{"operator": "stream", "operand" : "Slack"}, {"operator": "topic", "operand" : "test_channel"}]',
                  'apply_markdown': 'false'
                  }

        getNewestMessageRequest = get(zulipAuth['site'] + "/api/v1/messages", params=params, auth=(zulipAuth['email'], zulipAuth['key']))
        assert getNewestMessageRequest.status_code == 200

        # check that the message is present in the test_channel stream and that it has a certain message type
        getNewestMessageRequest = getNewestMessageRequest.json()
        assert getNewestMessageRequest['result'] == 'success' and 'messages' in getNewestMessageRequest, "Failed to retrieve messages from Zulip " + str(getNewestMessageRequest['msg'])

        # need to remove custom prefix
        userNameRequest = get(f"https://slack.com/api/users.info?{parse.urlencode({'user': userID})}", headers=slackAuth)
        assert userNameRequest.status_code == 200, "Requests failed to fetch :: https://slack.com/api/users.info"

        userNameRequest = userNameRequest.json()
        assert userNameRequest['ok'], "Failed to list channels, error :: " + str(userNameRequest['error'])

        content = getNewestMessageRequest['messages'][0]['content'].replace(slackCustomPrefix(userNameRequest['user'], "test_channel"), '', 1)
        assert getNewestMessageRequest['messages'][0]['subject'] == 'test_channel' and content == ' Test Message Event'


    def test_message_sending_zulip(self):
        # Create a zulip event
        createEvent = {'type': 'message', 'message': {'content': 'Test Message Event', 'subject': 'test_channel', 'sender_full_name': 'FR acc 1','sender_email': 'fenton.reid.2017@uni.strath.ac.uk','sender_realm_str': 'fenton','display_recipient': 'Slack','type': 'stream'}}
        createTopicEvent = zulipEvents([createEvent])
        assert createTopicEvent == "Message sent", "Slack could not create message"

        channelHistoryRequest = get("https://slack.com/api/conversations.history?" + parse.urlencode({"channel": getChannelID("test_channel"), "limit": 1}), headers=slackAuth)
        assert channelHistoryRequest.status_code == 200, "Requests failed to fetch :: https://slack.com/api/conversations.history"
        channelHistoryRequest = channelHistoryRequest.json()

        try:
            # need to remove custom prefix
            content = channelHistoryRequest['messages'][0]['text'].replace(zulipCustomPrefix(createEvent), '', 1)
            assert content == " Test Message Event"
        except:
            assert False, channelHistoryRequest


class TestEmojiAdditions:
    def test_emoji_additions_with_new_mapping_added(self):
        # Add to the current_user.emojiAdditions dictionary
        current_user.emojiAdditions = '{":heart_slack:" : ":heart_zulip:"}'

        # Create a zulip emoji message
        createEmojiMSG = {'type': 'message', 'message': {'content': 'New mapping added: :heart_zulip:', 'subject': 'test_channel', 'sender_full_name': 'FR acc 1', 'sender_email': 'fenton.reid.2017@uni.strath.ac.uk', 'sender_realm_str': 'fenton', 'display_recipient': 'Slack', 'type': 'stream'}}
        createEmojiEvent = zulipEvents([createEmojiMSG])
        assert createEmojiEvent == "Message sent", "Slack could not send message"

        channelHistoryRequest = get("https://slack.com/api/conversations.history?" + parse.urlencode({"channel": getChannelID("test_channel"), "limit": 1}), headers=slackAuth)
        assert channelHistoryRequest.status_code == 200, "Requests failed to fetch :: https://slack.com/api/conversations.history"
        channelHistoryRequest = channelHistoryRequest.json()

        try:
            content = channelHistoryRequest['messages'][0]['text'].replace(zulipCustomPrefix(createEmojiMSG), '', 1)
            assert content == " New mapping added: :heart_slack:"
        except:
            assert False, channelHistoryRequest

    def test_emoji_additions_with_new_mapping_removed(self):
        current_user.emojiAdditions = '{}'

        # Create a zulip emoji message
        createEmojiMSG = {'type': 'message', 'message': {'content': 'New mapping added: :heart:', 'subject': 'test_channel', 'sender_full_name': 'FR acc 1', 'sender_email': 'fenton.reid.2017@uni.strath.ac.uk', 'sender_realm_str': 'fenton', 'display_recipient': 'Slack', 'type': 'stream'}}
        createEmojiEvent = zulipEvents([createEmojiMSG])
        assert createEmojiEvent == "Message sent", "Slack could not send message"

        channelHistoryRequest = get("https://slack.com/api/conversations.history?" + parse.urlencode({"channel": getChannelID("test_channel"), "limit": 1}), headers=slackAuth)
        assert channelHistoryRequest.status_code == 200, "Requests failed to fetch :: https://slack.com/api/conversations.history"
        channelHistoryRequest = channelHistoryRequest.json()

        try:
            content = channelHistoryRequest['messages'][0]['text'].replace(zulipCustomPrefix(createEmojiMSG), '', 1)
            assert content == " New mapping added: "
        except:
            assert False, channelHistoryRequest


class TestRename:
    def test_rename_slack(self):
        # rename Zulip topic test_channel to test_channel_new
        renameChannelJSON = {'type': 'message', 'subtype': 'channel_name', 'old_name': 'test_channel', 'name': 'test_channel_new'}
        renameChannelEvent = slackEvents(renameChannelJSON)
        assert renameChannelEvent == "slack renamed a channel", "Zulip could not rename channel"
        
        # check in Zulip that the latest message has topic named `test_channel_new`
        params = {'anchor': 'newest',
                  'num_before': 1, 'num_after': 0,
                  'narrow': '[{"operator": "stream", "operand" : "Slack"}, {"operator": "topic", "operand" : "test_channel_new"}]',
                  'apply_markdown': 'false'
                  }

        getNewestMessageRequest = get(zulipAuth['site'] + "/api/v1/messages", params=params, auth=(zulipAuth['email'], zulipAuth['key']))
        assert getNewestMessageRequest.status_code == 200

        getNewestMessageRequest = getNewestMessageRequest.json()

        # check that the message is present in the test_channel stream and that it has a certain message type
        assert getNewestMessageRequest['result'] == 'success' and 'messages' in getNewestMessageRequest, "Failed to retrieve messages from Zulip " + str(getNewestMessageRequest['msg'])
        assert 'test_channel_new' == getNewestMessageRequest['messages'][0]['subject']


    def test_rename_invalid_zulip(self): # set test_channel in Slack to (test_channel_invalid) and check for correct rename
        # Create a Zulip rename event
        renameTopicJSON = [{'type': 'update_message', 'orig_subject': 'test_channel', 'subject': '(test_channel_invalid)', 'message_type': 'stream', 'sender_email': 'integration-bot-bot@zulipchat.com'}]
        renameTopicEvent = zulipEvents(renameTopicJSON)
        assert renameTopicEvent == "Zulip renamed a Slack channel", "Zulip could not rename Slack channel"

        # check in Slack that the test_channel_new channel exists
        listChannelsRequest = get( "https://slack.com/api/conversations.list?" + parse.urlencode({"exclude_archived": True, "limit": 1000}), headers=slackAuth)
        assert listChannelsRequest.status_code == 200, "Requests failed to fetch :: https://slack.com/api/conversations.list"

        listChannelsRequest = listChannelsRequest.json()
        assert listChannelsRequest['ok'], "Failed to list channels, error :: " + str(listChannelsRequest['error'])
        assert ('channels' in listChannelsRequest and len( listChannelsRequest['channels']) == 2), "general and test_channel in the Slack workplace"
        assert next((current['name'] for current in listChannelsRequest['channels'] if current['name'] == 'test_channel_invalid'), '') == 'test_channel_invalid'


    def test_rename_valid_zulip(self):
        # Create a Zulip rename event
        renameTopicJSON = [{'type': 'update_message', 'orig_subject' : 'test_channel_invalid', 'subject' : 'test_channel_new', 'message_type': 'stream', 'sender_email' : 'integration-bot-bot@zulipchat.com'}]
        renameTopicEvent = zulipEvents(renameTopicJSON)
        assert renameTopicEvent == "Zulip renamed a Slack channel", "Zulip could not rename Slack channel"

        # check in Slack that the test_channel_new channel exists
        listChannelsRequest = get("https://slack.com/api/conversations.list?" + parse.urlencode({"exclude_archived" : True, "limit" : 1000}), headers=slackAuth)
        assert listChannelsRequest.status_code == 200, "Requests failed to fetch :: https://slack.com/api/conversations.list"

        listChannelsRequest = listChannelsRequest.json()
        assert listChannelsRequest['ok'], "Failed to list channels, error :: " + str(listChannelsRequest['error'])
        assert ('channels' in listChannelsRequest and len(listChannelsRequest['channels']) == 2), "general and test_channel in the Slack workplace"
        assert next((current['name'] for current in listChannelsRequest['channels'] if current['name'] == 'test_channel_new'), '') == 'test_channel_new'


class TestSlackGeneralChannelRename:
    def test_rename_slack(self):
        # rename Zulip topic test_channel to test_channel_new
        renameChannelJSON = {'type': 'message', 'subtype': 'channel_name', 'old_name': 'general', 'name': 'general1'}
        renameChannelEvent = slackEvents(renameChannelJSON)
        assert renameChannelEvent == "slack renamed a channel", "Zulip could not rename channel"

        # check in Slack that the test_channel_new channel exists
        listChannelsRequest = get("https://slack.com/api/conversations.list?" + parse.urlencode({"exclude_archived": True, "limit": 1000}), headers=slackAuth)
        assert listChannelsRequest.status_code == 200, "Requests failed to fetch :: https://slack.com/api/conversations.list"

        listChannelsRequest = listChannelsRequest.json()
        assert listChannelsRequest['ok'], "Failed to list channels, error :: " + str(listChannelsRequest['error'])
        assert ('channels' in listChannelsRequest and len(listChannelsRequest['channels']) == 2), "general and test_channel in the Slack workplace"
        assert next((current['name'] for current in listChannelsRequest['channels'] if current['name'] == 'general'), '') == 'general'

        # assert that the last message is: You cannot rename the general chat!
        channelHistoryRequest = get("https://slack.com/api/conversations.history?" + parse.urlencode({"channel": getChannelID("general"), "limit": 1}), headers=slackAuth)
        assert channelHistoryRequest.status_code == 200, "Requests failed to fetch :: https://slack.com/api/conversations.history"
        channelHistoryRequest = channelHistoryRequest.json()
        assert channelHistoryRequest['messages'][0]['text'] == "You cannot rename the general chat!"


class TestDelete:
    def test_delete_slack(self):
        session['slackChannels'][getChannelID('test_channel_new')] = 'test_channel_new'
        deletedChannelID = getChannelID('test_channel_new')
        deleteChannel('test_channel_new')
        deleteChannelJSON = {'type': 'channel_deleted', 'channel' : deletedChannelID}
        deleteChannelEvent = slackEvents(deleteChannelJSON)
        assert deleteChannelEvent == "Slack deleted a channel", "Zulip could not delete channel"

        # check that test_channel_new was deleted
        zulipTopics = get(zulipAuth['site'] + f"/api/v1/users/me/{getSlackStreamID()}/topics", auth=(zulipAuth['email'], zulipAuth['key']))
        assert zulipTopics.status_code == 200, "Request failed to fetch :: https://yourZulipDomain.zulipchat.com/api/v1/users/me/{stream_id}/topics"

        zulipTopics = zulipTopics.json()
        assert 'result' in zulipTopics and 'topics' in zulipTopics, "Zulip failed to return a list of topics in the Slack stream " + str(zulipTopics['error'])
        assert list(filter(lambda x: x['name'] == 'test_channel_new', zulipTopics['topics'])) == [], "Zulip found test_channel_new in the Slack stream"


    def test_delete_zulip(self):
        createSlackTestChannel()

        deleteTopicJSON = [{'type': 'delete_message', 'stream_id': getSlackStreamID(), 'topic': 'test_channel', 'message_type': 'stream', 'sender_email': 'integration-bot-bot@zulipchat.com'}]
        deleteTopicEvent = zulipEvents(deleteTopicJSON)
        assert deleteTopicEvent == "Zulip deleted a Slack channel", "Slack could not delete channel"

        # Check Slack
        listChannelsRequest = get("https://slack.com/api/conversations.list?" + parse.urlencode({"exclude_archived" : True, "limit" : 1000}), headers=slackAuth)
        assert listChannelsRequest.status_code == 200, "Requests failed to fetch :: https://slack.com/api/conversations.list"

        listChannelsRequest = listChannelsRequest.json()
        assert listChannelsRequest['ok'], "Failed to list channels, error :: " + str(listChannelsRequest['error'])
        assert next((current['name'] for current in listChannelsRequest['channels'] if current['name'] == 'test_channel'), '') == ''