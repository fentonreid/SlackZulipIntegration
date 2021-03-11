from requests import get
from urllib import parse
from pytest import fixture
from integration.events.slackEvents import slackCustomPrefix
from integration.markdown.toSlack import slackMarkdown
from integration.startup.utilities import parseZulipRC
from tests.integration.test_integration import slackAuth, userEmailList
from flask_login import current_user


@fixture
def singleTag():
    return "This is a single markdown "

@fixture
def fullUrl():
    return "http://www.google.com"

@fixture
def shortUrl():
    return "www.google.com"

@fixture
def eventData():
    userID, _ = userEmailList()
    userNameRequest = get(f"https://slack.com/api/users.info?{parse.urlencode({'user': userID})}", headers=slackAuth)
    userNameRequest = userNameRequest.json()

    return userNameRequest['user'], "test_channel"


class TestBold:
    def test_singleBold(self, singleTag):
        assert slackMarkdown(singleTag + "**tag**") == ('This is a single markdown *tag*', [])

    def test_multipleBold(self, singleTag):
        assert slackMarkdown(singleTag + "**tag** and this is **another**") == ('This is a single markdown *tag* and this is *another*', [])

    def test_incompleteBold(self):
        assert slackMarkdown("This is an incomplete **bold tag") == ('This is an incomplete **bold tag', [])

    def test_multilineBold(self):
        assert slackMarkdown("This is a **multi-line\n bold tag**") == ('This is a **multi-line\n bold tag**', [])


class TestItalics:
    def test_singleItalic(self, singleTag):
        assert slackMarkdown(singleTag + "*tag*") == ('This is a single markdown _tag_', [])

    def test_multipleItalics(self, singleTag):
        assert slackMarkdown(singleTag + "*tag* and this is *another*") == ('This is a single markdown _tag_ and this is _another_', [])

    def test_incompleteItalic(self):
        assert slackMarkdown("This is an incomplete *bold tag") == ('This is an incomplete *bold tag', [])

    def test_multilineItalic(self):
        assert slackMarkdown("This is a *multi-line\n italic tag*") == ('This is a *multi-line\n italic tag*', [])


class TestStrike:
    def test_singleStrike(self, singleTag):
        assert slackMarkdown(singleTag + "~~tag~~") == ('This is a single markdown ~tag~', [])

    def test_multipleStrike(self, singleTag):
        assert slackMarkdown(singleTag + "~~tag~~ and this is ~~another~~") == ('This is a single markdown ~tag~ and this is ~another~', [])

    def test_incompleteStrike(self):
        assert slackMarkdown("This is an incomplete ~~strike tag") == ('This is an incomplete ~~strike tag', [])

    def test_multilineStrike(self):
        assert slackMarkdown("This is a ~~multi-line\n strike tag~~") == ('This is a ~~multi-line\n strike tag~~', [])


class TestBISCombination:
    def test_BoldItalic(self):
        assert slackMarkdown("This is a ***bold italic*** combination") == ('This is a *_bold italic_* combination', [])

    def test_BoldStrike(self):
        assert slackMarkdown("This is a **~~bold strike~~** combination") == ('This is a *~bold strike~* combination', [])

    def test_ItalicBold(self):
        assert slackMarkdown("This is a ***italic bold*** combination") == ('This is a *_italic bold_* combination', [])

    def test_ItalicStrike(self):
        assert slackMarkdown("This is a *~~italic strike~~* combination") == ('This is a _~italic strike~_ combination', [])

    def test_StrikeBold(self):
        assert slackMarkdown("This is a ~~**strike bold**~~ combination") == ('This is a ~*strike bold*~ combination', [])

    def test_StrikeItalic(self):
        assert slackMarkdown("This is a ~~*strike italic*~~ combination") == ('This is a ~_strike italic_~ combination', [])

    def test_BoldItalicStrike(self):
        assert slackMarkdown("This is a ***~~bold italic strike~~*** combination") == ('This is a *_~bold italic strike~_* combination', [])

    def test_AllMultiline(self):
        assert slackMarkdown("This is ***~~multi-line\n tag test~~***") == ('This is ***~~multi-line\n tag test~~***', [])

class TestQuotes:
    def test_Quotes(self):
        assert slackMarkdown("> This is a quote\nso is this\nand this\n\n") == ('\n> This is a quote\n>so is this\n>and this\n\n', [])
        assert slackMarkdown("> This is a quote\nso is this\n\nthis isn't!") == ('\n> This is a quote\n>so is this\n\nthis isn\'t!', [])


class TestBlockQuote:
    def test_BlockQuotes(self):
        assert slackMarkdown("```quote\nThis is a quote\nso is this\n```") == ('\n>This is a quote\n>so is this\n', [])
        assert slackMarkdown("```quote\nThis is a quote\nso is this\n```\n\nThis is normal text") == ('\n>This is a quote\n>so is this\n\n\nThis is normal text', [])


class TestInlineCode:
    def test_InlineCode(self):
        assert slackMarkdown("`Inline code`") == ('`Inline code`', [])
        assert slackMarkdown("```Inline code```") == ('`Inline code`', [])
        assert slackMarkdown("    Inline code") == ('`Inline code`', [])
        assert slackMarkdown("     Inline code") == ('` Inline code`', [])
        assert slackMarkdown("~~~Inline code~~~") == ('`Inline code`', [])


class TestMultiLineCode:
    def test_MultiLineCode_Text(self):
        assert slackMarkdown("```text\nThis is a code block\nso is this\n```") == ("```\nThis is a code block\nso is this\n```", [])
        assert slackMarkdown("~~~text\nThis is a code block\nso is this\n~~~") == ("```\nThis is a code block\nso is this\n```", [])
        assert slackMarkdown("```text\nThis is a code block\nso is this\n```\n\nMore normal text") == ("```\nThis is a code block\nso is this\n```\n\nMore normal text", [])
        assert slackMarkdown("~~~text\nThis is a code block\nso is this\n~~~\n\nMore normal text") == ("```\nThis is a code block\nso is this\n```\n\nMore normal text", [])

    def test_MultiLineCode_Empty(self):
        assert slackMarkdown("```\nThis is a code block\nso is this\n```") == ("```\nThis is a code block\nso is this\n```", [])
        assert slackMarkdown("~~~\nThis is a code block\nso is this\n~~~") == ("```\nThis is a code block\nso is this\n```", [])
        assert slackMarkdown("```\nThis is a code block\nso is this\n```\n\nMore normal text") == ("```\nThis is a code block\nso is this\n```\n\nMore normal text", [])
        assert slackMarkdown("~~~\nThis is a code block\nso is this\n~~~\n\nMore normal text") == ("```\nThis is a code block\nso is this\n```\n\nMore normal text", [])

    def test_MultiLineCode_Other(self):
        assert slackMarkdown("```python\nThis is a code block\nso is this\n```") == ("```\nThis is a code block\nso is this\n```", [])
        assert slackMarkdown("~~~python\nThis is a code block\nso is this\n~~~") == ("```\nThis is a code block\nso is this\n```", [])
        assert slackMarkdown("```python\nThis is a code block\nso is this\n```\n\nMore normal text") == ("```\nThis is a code block\nso is this\n```\n\nMore normal text", [])
        assert slackMarkdown("~~~python\nThis is a code block\nso is this\n~~~\n\nMore normal text") == ("```\nThis is a code block\nso is this\n```\n\nMore normal text", [])


class TestBulletLists:
    def test_BulletList(self):
        assert slackMarkdown("- bullet 1\n- bullet 2") == ('\n- bullet 1\n- bullet 2', [])
        assert slackMarkdown("   -     bullet 1\n   -     bullet 2") == ('\n- bullet 1\n- bullet 2', [])
        assert slackMarkdown("+ bullet 1\n+ bullet 2") == ('\n- bullet 1\n- bullet 2', [])
        assert slackMarkdown("* bullet 1\n* bullet 2") == ('\n- bullet 1\n- bullet 2', [])


class TestNumberedList:
    def test_NumberedList(self):
        assert slackMarkdown("1. bullet 1\n1. bullet this is") == ('\n1. bullet 1\n2. bullet this is', [])
        assert slackMarkdown("  1. bullet 1\n  1. bullet this is") == ('\n1. bullet 1\n2. bullet this is', [])
        assert slackMarkdown("   1. bullet 1\n   1. bullet this is") == ('\n1. bullet 1\n2. bullet this is', [])
        assert slackMarkdown("1. bullet 1\n1. bullet this is\n\nNormal text") == ('\n1. bullet 1\n2. bullet this is\n\nNormal text', [])


class TestWebsiteLink:
    def test_EmbeddedLink(self, fullUrl, shortUrl):
        assert slackMarkdown("This is a link " + fullUrl) == ('This is a link ' + fullUrl, [])
        assert slackMarkdown("This is a link " + shortUrl) == ('This is a link ' + shortUrl, [])


    def test_TextWithLink(self, fullUrl, shortUrl):
        assert slackMarkdown('This is a link [homepage](' + fullUrl + ')') == ("This is a link <" + fullUrl + "|homepage>", [])
        assert slackMarkdown("This is a link [" + shortUrl + "](" + fullUrl + ")") == ('This is a link <' + fullUrl + '|' + shortUrl + '>', [])
        # short url's are converted by slack automatically, hence no short link test


class TestFileUploads:
    def test_SingleFileUpload(self):
        assert slackMarkdown("This is a single file upload [testFile](/user_uploads/testFile.png)") == ('This is a single file upload ', [('testFile', parseZulipRC(current_user.zulipBotRC)['site'] + '/user_uploads/testFile.png')])

    def test_MultipleFileUploads(self):
        assert slackMarkdown("This is a multiple file upload[testFile1](/user_uploads/testFile1.png)[testFile2](/user_uploads/testFile2.png)") == ('This is a multiple file upload', [('testFile1',  parseZulipRC(current_user.zulipBotRC)['site'] + '/user_uploads/testFile1.png'), ('testFile2',  parseZulipRC(current_user.zulipBotRC)['site'] + '/user_uploads/testFile2.png')])


class TestPrefix:
    class TestPrefix:
        def test_namePrefix(self, eventData):
            assert slackCustomPrefix(eventData[0], eventData[1], testing='Sent from {name} |') == "Sent from " + eventData[0]['real_name'] + " |"

        def test_emailPrefix(self, eventData):
            assert slackCustomPrefix(eventData[0], eventData[1], testing='Sent from {email} |') == "Sent from " + eventData[0]['profile']['email'] + " |"

        def test_channelPrefix(self, eventData):
            assert slackCustomPrefix(eventData[0], eventData[1], testing='Sent from {channel} |') == "Sent from " + eventData[1] +" |"

        def test_multipleTypesPrefix(self, eventData):
            assert slackCustomPrefix(eventData[0], eventData[1], testing='📢 sent to {channel} by {name} |') == "📢 sent to test_channel by " + eventData[0]['real_name']+ " |"