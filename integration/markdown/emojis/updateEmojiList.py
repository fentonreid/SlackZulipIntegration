import os
import sys

from requests import get

sys.path.append("\\".join(os.getcwd().split("\\")[:-3]))

from integration.markdown.emojis.shortCodeDict import getCommonEmojis
# code to automatically upload the emojiList found in shortCodeDict.py

# PRINT THE FOLLOWING CODE FROM GITHUB
emoji_names = get("https://raw.githubusercontent.com/zulip/zulip/master/tools/setup/emoji/emoji_names.py")
print(emoji_names.content.decode())
# get the user input
print("\nThe following code from, https://raw.githubusercontent.com/zulip/zulip/master/tools/setup/emoji/emoji_names.py has been printed above. Does this seem safe?\n")
userConsent = str(input("Do you want to proceed (y/n): "))

if userConsent in ['y', 'Y', 'yes', 'YES']:
    print("UPDATING")
    tupleResult = getCommonEmojis()

    if str(type(tupleResult[1])).find("list"):
        # get current contents of shortCodeDict.py
        with open('shortCodeDict.py', 'r', encoding="utf8") as scd:
            contents = scd.readlines()

        # update emojiList
        with open('shortCodeDict.py', 'w', encoding="utf8") as scd:
            for count, line in enumerate(contents):
                if line.find("return [") > -1:
                    contents[count] = "    return " + str(tupleResult[1]) + "\n"
                    break

        # update Slack To Zulip Dict
        with open('shortCodeDict.py', 'w', encoding="utf8") as scd:
            counter = 0
            for count, line in enumerate(contents):
                if line.find("return {") > -1:
                    counter += 1

                if counter == 3:
                    contents[count] = "    return " + str(tupleResult[0]) + "\n"
                    break

            scd.writelines(contents)
else:
    print("STOPPING WITHOUT EXECUTION")
