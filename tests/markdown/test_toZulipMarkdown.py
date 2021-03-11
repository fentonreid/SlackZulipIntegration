from pytest import fixture
from integration.events.slackEvents import handleFiles
from integration.events.zulipEvents import zulipCustomPrefix
from integration.markdown.toZulip import zulipMarkdown

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
def event():
    return {'type': 'message', 'message': {'content': 'Test Message Event', 'subject': 'test_channel', 'sender_full_name': 'FR acc 1', 'sender_email': 'fenton.reid.2017@uni.strath.ac.uk', 'sender_realm_str': 'fenton', 'display_recipient': 'Slack', 'type': 'stream'}}


class TestBold:
    def test_singleBold(self, singleTag):
        assert zulipMarkdown(singleTag + "*tag*") == ('This is a single markdown **tag**', [])

    def test_multipleBold(self, singleTag):
        assert zulipMarkdown(singleTag + "*tag* and this is *another*") == ('This is a single markdown **tag** and this is **another**', [])

    def test_incompleteBold(self):
        assert zulipMarkdown("This is an incomplete *bold tag") == ('This is an incomplete *bold tag', [])

    def test_multilineBold(self):
        assert zulipMarkdown("This is a *multi-line\n bold tag*") == ('This is a *multi-line\n bold tag*', [])

class TestItalics:
    def test_singleItalic(self, singleTag):
        assert zulipMarkdown(singleTag + "_tag_") == ('This is a single markdown *tag*', [])

    def test_multipleItalics(self, singleTag):
        assert zulipMarkdown(singleTag + "_tag_ and this is _another_") == ('This is a single markdown *tag* and this is *another*', [])

    def test_incompleteItalic(self):
        assert zulipMarkdown("This is an incomplete _bold tag") == ('This is an incomplete _bold tag', [])

    def test_multilineItalic(self):
        assert zulipMarkdown("This is a _multi-line\n italic tag_") == ('This is a _multi-line\n italic tag_', [])


class TestStrike:
    def test_singleStrike(self, singleTag):
        assert zulipMarkdown(singleTag + "~tag~") == ('This is a single markdown ~~tag~~', [])

    def test_multipleStrike(self, singleTag):
        assert zulipMarkdown(singleTag + "~tag~ and this is ~another~") == ('This is a single markdown ~~tag~~ and this is ~~another~~', [])

    def test_incompleteStrike(self):
        assert zulipMarkdown("This is an incomplete ~strike tag") == ('This is an incomplete ~strike tag', [])

    def test_multilineStrike(self):
        assert zulipMarkdown("This is a ~multi-line\n strike tag~") == ('This is a ~multi-line\n strike tag~', [])


class TestBISCombination:
    def test_BoldItalic(self):
        assert zulipMarkdown("This is a *_bold italic_* combination") == ('This is a ***bold italic*** combination', [])

    def test_BoldStrike(self):
        assert zulipMarkdown("This is a *~bold strike~* combination") == ('This is a **~~bold strike~~** combination', [])

    def test_ItalicBold(self):
        assert zulipMarkdown("This is a *_italic bold_* combination") == ('This is a ***italic bold*** combination', [])

    def test_ItalicStrike(self):
        assert zulipMarkdown("This is a _~italic strike~_ combination") == ('This is a *~~italic strike~~* combination', [])

    def test_StrikeBold(self):
        assert zulipMarkdown("This is a ~*strike bold*~ combination") == ('This is a ~~**strike bold**~~ combination', [])

    def test_StrikeItalic(self):
        assert zulipMarkdown("This is a ~_strike italic_~ combination") == ('This is a ~~*strike italic*~~ combination', [])

    def test_BoldItalicStrike(self):
        assert zulipMarkdown("This is a *_~bold italic strike~_* combination") == ('This is a ***~~bold italic strike~~*** combination', [])

    def test_AllMultiline(self):
        assert zulipMarkdown("This is *_~multi-line\n tag test~_*") == ('This is *_~multi-line\n tag test~_*', [])


class TestQuotes:
    def test_Quotes(self):
        assert zulipMarkdown("> This is a quote\n>so is this\n>and this\n\n") == ('\n>This is a quote\n>so is this\n>and this\n\n', [])
        assert zulipMarkdown("   > This is a quote\n   >    so is this\n   >    and this\n\n") == ('\n>This is a quote\n>so is this\n>and this\n\n', [])


class TestInlineCode:
    def test_InlineCode(self):
        assert zulipMarkdown("`Inline code`") == ('`Inline code`', [])


class TestMultiLineCode:
    def test_MultiLineCode(self):
        assert zulipMarkdown("```Multi line code```") == ('\n```\nMulti line code\n```', [])
        assert zulipMarkdown("```\nMulti line code\n```") == ('\n```\nMulti line code\n```', [])


class TestBulletLists:
    def test_BulletList(self):
        assert zulipMarkdown("* Bullet 1\n* Bullet 2") == ('\n- Bullet 1\n- Bullet 2', [])
        assert zulipMarkdown("+ Bullet 1\n+ Bullet 2") == ('\n- Bullet 1\n- Bullet 2', [])
        assert zulipMarkdown("- Bullet 1\n- Bullet 2") == ('\n- Bullet 1\n- Bullet 2', [])

        assert zulipMarkdown("*Bullet 1\n*Bullet 2") == ('\n- Bullet 1\n- Bullet 2', [])
        assert zulipMarkdown("+Bullet 1\n+Bullet 2") == ('\n- Bullet 1\n- Bullet 2', [])
        assert zulipMarkdown("-Bullet 1\n-Bullet 2") == ('\n- Bullet 1\n- Bullet 2', [])


class TestWebsiteLink:
    def test_BasicMarkdownLink(self, fullUrl):
        assert zulipMarkdown("This is a link <" + fullUrl + ">") == ('This is a link ' + fullUrl, [])

    def test_ComplexMarkdownLink(self, fullUrl, shortUrl):
        assert zulipMarkdown("This is a link <" + fullUrl + "|homepage>") == ('This is a link [homepage](' + fullUrl + ')', [])
        assert zulipMarkdown("This is a link <" + fullUrl + "|" + shortUrl + ">") == ('This is a link [' + shortUrl + '](' + fullUrl + ')', [])
        # short url's are converted by slack automatically, hence no short link test


class TestFileUploads:
    def test_SingleFileUpload(self):
        # this event mimics the slack event that will be handled
        assert handleFiles([{'name' : "test1.txt", "url_private" : "http://www.fentonreid.pythonanywhere.com/test1.txt"}]) == [('test1.txt', 'http://www.fentonreid.pythonanywhere.com/test1.txt')]

    def test_MultipleFileUploads(self):
        assert handleFiles([{'name': "test1.txt", "url_private": "http://www.fentonreid.pythonanywhere.com/test1.txt"}, {'name': "test2.txt", "url_private": "http://www.fentonreid.pythonanywhere.com/test2.txt"}]) == [('test1.txt', 'http://www.fentonreid.pythonanywhere.com/test1.txt'), ('test2.txt', 'http://www.fentonreid.pythonanywhere.com/test2.txt')]

class TestPrefix:
    def test_namePrefix(self, event):
        assert zulipCustomPrefix(event, testing='Sent from {name} |') == "Sent from FR acc 1 |"

    def test_emailPrefix(self, event):
        assert zulipCustomPrefix(event, testing='Sent from {email} |') == "Sent from fenton.reid.2017@uni.strath.ac.uk |"

    def test_channelPrefix(self, event):
        assert zulipCustomPrefix(event, testing='Sent from {channel} |') == "Sent from test_channel |"

    def test_multipleTypesPrefix(self, event):
        assert zulipCustomPrefix(event, testing='📢 sent to {channel} by {name} |') == "📢 sent to test_channel by FR acc 1 |"

