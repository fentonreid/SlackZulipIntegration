def parseZulipRC(zulipRC):
    """
    Generate dictionary for Zulip API based on a given zulipRC.

    :param zulipRC: Unique identifier for a user/bot in Zulip
    :type zulipRC: String
    """
    lines = (zulipRC + " ").split(" ")
    try:
        return {"email": lines[1][6:], "key": lines[2][4:], "site": lines[3][5:]}
    except:
        return None


def slackHeader(token):
    """
    Generate custom header for Slack API requests based on a given Slack Token

    :param token: Unique identified for a user/bot in Slack
    :type token: String
    """
    return {"Authorization": "Bearer " + token}