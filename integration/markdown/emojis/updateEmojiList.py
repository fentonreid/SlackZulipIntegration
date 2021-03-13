from integration.markdown.emojis.shortCodeDict import getCommonEmojis
# code to automatically upload the emojiList found in shortCodeDict.py

newEmojiList = getCommonEmojis()[1]

if str(type(newEmojiList)).find("list"):
    # get current contents of shortCodeDict.py
    with open('shortCodeDict.py', 'r', encoding="utf8") as scd:
        contents = scd.readlines()
        duplicate = scd.readlines()

    with open('shortCodeDict.py', 'w', encoding="utf8") as scd:
        for count, line in enumerate(contents):
            if line.find("return [") > -1:
                contents[count] = "    return " + str(newEmojiList) + "\n"
                break

        scd.writelines(contents)