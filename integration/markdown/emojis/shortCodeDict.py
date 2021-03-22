# -*- coding: utf-8 -*-
from requests import get


def unicodePoint(val):
    """
    Converts a shortened unicode value into a standard UTF-8 format by the addition of padding.

    :param val: Shortened code point
    :type val: Unicode point
    """
    if val == "":
        return
    # the possible multiple unicode values into a list
    unicodePointList = val.split("-")
    uP = ""
    for point in unicodePointList:
        # add extras 0's to make it a complete Unicode code point
        padding = ("0" * (8 - len(point)))
        # return unicode emoji back by concatenating
        uP += ((r"\U" + padding + point).encode("utf-8")).decode('unicode-escape')
    return uP


def slackDict():
    """
    Fetch the emoji.json file from https://raw.githubusercontent.com/iamcal/emoji-data/master/emoji.json.
    Parse the json file and collect the unicode points for each emoji in this file.
    Return a dictionary of unicode points to short codes.
    """
    slackJSON = get("https://raw.githubusercontent.com/iamcal/emoji-data/master/emoji.json").json()
    return {unicodePoint(emoji['unified']) :  ':' + emoji['short_name'] + ':' for emoji in slackJSON}


def zulipDict():
    """
    Makes a get response to the Zulip GitHub: emoji_names.py file, https://raw.githubusercontent.com/zulip/zulip/master/tools/setup/emoji/emoji_names.py.
    exec the emoji_names.py file and convert the typing dictionary into a Zulip dictionary of codepoints as keys and shortcodes as values.
    """
    emoji_names = get("https://raw.githubusercontent.com/zulip/zulip/master/tools/setup/emoji/emoji_names.py")

    # modify the github code to return the EMOJI_NAME_MAPS dictionary
    resultDictionary = {}
    exec(emoji_names.content, locals(), resultDictionary)
    emoji_dictionary = resultDictionary['EMOJI_NAME_MAPS']

    return {unicodePoint(entry) :  ":" + emoji_dictionary[entry]['canonical_name'] + ":" for entry in emoji_dictionary}



def getCommonEmojis():
    """
    Using the slack and zulip dictionaries as defined above, create a dictionary of slack to zulip shortcodes of emojis that are present in both.
    """
    sD = slackDict()
    zD = zulipDict()

    shortCodes = {}
    emojiList = []

    for sItem in sD:
        if sItem in zD:
            for zItem in zD:
                if sItem == zItem:
                    emojiList.append(sItem)
                    shortCodes[sD[sItem]] = zD[zItem]

    return shortCodes, emojiList


def emojiList():
    """
    A full list of emojis found in both Slack and Zulip, need for the customPrefixes.html file.
    The second element in the getCommonEmojis() output.
    """
    return ['🀄', '🃏', '🆎', '🆑', '🆒', '🆓', '🆔', '🆕', '🆖', '🆗', '🆘', '🆙', '🆚', '🌀', '🌁', '🌂', '🌃', '🌄', '🌅', '🌆', '🌇', '🌈', '🌉', '🌊', '🌋', '🌌', '🌍', '🌎', '🌏', '🌐', '🌑', '🌔', '🌕', '🌙', '🌚', '🌛', '🌝', '🌞', '🌟', '🌠', '🌭', '🌮', '🌯', '🌰', '🌱', '🌲', '🌳', '🌴', '🌵', '🌷', '🌸', '🌹', '🌺', '🌻', '🌼', '🌽', '🌾', '🌿', '🍀', '🍁', '🍂', '🍃', '🍄', '🍅', '🍆', '🍇', '🍈', '🍉', '🍊', '🍋', '🍌', '🍍', '🍎', '🍏', '🍐', '🍑', '🍒', '🍓', '🍔', '🍕', '🍖', '🍗', '🍘', '🍙', '🍚', '🍛', '🍜', '🍝', '🍞', '🍟', '🍠', '🍡', '🍢', '🍣', '🍤', '🍥', '🍦', '🍧', '🍨', '🍩', '🍪', '🍫', '🍬', '🍭', '🍮', '🍯', '🍰', '🍱', '🍲', '🍳', '🍴', '🍵', '🍶', '🍷', '🍸', '🍹', '🍺', '🍻', '🍼', '🍾', '🍿', '🎀', '🎁', '🎂', '🎃', '🎄', '🎅', '🎆', '🎇', '🎈', '🎉', '🎊', '🎋', '🎌', '🎍', '🎎', '🎏', '🎐', '🎑', '🎒', '🎓', '🎠', '🎡', '🎢', '🎣', '🎤', '🎥', '🎦', '🎧', '🎨', '🎩', '🎪', '🎫', '🎬', '🎭', '🎮', '🎯', '🎰', '🎱', '🎲', '🎳', '🎴', '🎵', '🎶', '🎷', '🎸', '🎹', '🎺', '🎻', '🎼', '🎽', '🎾', '🎿', '🏀', '🏁', '🏂', '🏃', '🏄', '🏅', '🏆', '🏇', '🏈', '🏉', '🏊', '🏏', '🏐', '🏑', '🏒', '🏓', '🏠', '🏡', '🏢', '🏣', '🏤', '🏥', '🏦', '🏧', '🏨', '🏩', '🏪', '🏫', '🏬', '🏭', '🏮', '🏯', '🏰', '🏴', '🏸', '🏹', '🏺', '🐀', '🐁', '🐂', '🐃', '🐄', '🐅', '🐆', '🐇', '🐈', '🐉', '🐊', '🐋', '🐌', '🐍', '🐎', '🐏', '🐐', '🐑', '🐒', '🐓', '🐔', '🐕', '🐖', '🐗', '🐘', '🐙', '🐚', '🐛', '🐜', '🐝', '🐞', '🐟', '🐠', '🐡', '🐢', '🐣', '🐤', '🐥', '🐦', '🐧', '🐨', '🐩', '🐪', '🐫', '🐬', '🐭', '🐮', '🐯', '🐰', '🐱', '🐲', '🐳', '🐴', '🐵', '🐶', '🐷', '🐸', '🐹', '🐺', '🐻', '🐼', '🐽', '🐾', '👀', '👂', '👃', '👄', '👅', '👆', '👇', '👈', '👉', '👊', '👋', '👌', '👍', '👎', '👏', '👐', '👑', '👒', '👓', '👔', '👕', '👖', '👗', '👘', '👙', '👚', '👛', '👜', '👝', '👞', '👟', '👠', '👡', '👢', '👣', '👤', '👥', '👦', '👧', '👨', '👩', '👪', '👫', '👬', '👭', '👮', '👯', '👰', '👲', '👳', '👴', '👵', '👶', '👷', '👸', '👹', '👺', '👻', '👼', '👽', '👾', '👿', '💀', '💁', '💂', '💃', '💄', '💅', '💆', '💇', '💈', '💉', '💊', '💋', '💌', '💍', '💎', '💐', '💒', '💓', '💔', '💕', '💖', '💗', '💘', '💙', '💚', '💛', '💜', '💝', '💞', '💟', '💠', '💡', '💢', '💣', '💤', '💥', '💦', '💧', '💨', '💩', '💪', '💫', '💬', '💭', '💮', '💯', '💰', '💱', '💲', '💳', '💴', '💵', '💶', '💷', '💸', '💹', '💺', '💻', '💼', '💽', '💾', '💿', '📀', '📁', '📂', '📃', '📄', '📅', '📆', '📇', '📈', '📉', '📊', '📋', '📌', '📍', '📎', '📏', '📐', '📑', '📒', '📓', '📔', '📕', '📖', '📗', '📘', '📙', '📚', '📛', '📜', '📝', '📞', '📟', '📠', '📡', '📢', '📣', '📤', '📥', '📦', '📧', '📨', '📩', '📪', '📫', '📬', '📭', '📮', '📯', '📰', '📱', '📲', '📳', '📴', '📵', '📶', '📷', '📸', '📹', '📺', '📻', '📼', '📿', '🔀', '🔁', '🔂', '🔃', '🔄', '🔅', '🔆', '🔇', '🔈', '🔉', '🔊', '🔋', '🔌', '🔍', '🔏', '🔐', '🔑', '🔒', '🔓', '🔔', '🔕', '🔖', '🔗', '🔘', '🔙', '🔚', '🔛', '🔜', '🔝', '🔞', '🔟', '🔠', '🔡', '🔢', '🔣', '🔤', '🔥', '🔦', '🔧', '🔨', '🔩', '🔪', '🔫', '🔬', '🔭', '🔮', '🔰', '🔱', '🔲', '🔳', '🔴', '🔵', '🔶', '🔷', '🔸', '🔹', '🔺', '🔻', '🔼', '🔽', '🕋', '🕌', '🕍', '🕎', '🕗', '🕺', '🖕', '🖖', '🖤', '🗻', '🗼', '🗽', '🗾', '🗿', '😀', '😁', '😂', '😃', '😄', '😅', '😆', '😇', '😈', '😉', '😊', '😋', '😌', '😍', '😎', '😏', '😐', '😑', '😒', '😓', '😔', '😕', '😖', '😗', '😘', '😙', '😚', '😛', '😜', '😝', '😞', '😟', '😠', '😡', '😢', '😣', '😤', '😥', '😦', '😧', '😨', '😩', '😪', '😫', '😬', '😭', '😮', '😯', '😰', '😱', '😲', '😳', '😴', '😵', '😶', '😷', '😸', '😹', '😺', '😻', '😼', '😽', '😾', '😿', '🙀', '🙁', '🙂', '🙃', '🙄', '🙅', '🙆', '🙇', '🙈', '🙉', '🙊', '🙋', '🙌', '🙍', '🙎', '🙏', '🚀', '🚁', '🚂', '🚃', '🚄', '🚅', '🚆', '🚇', '🚈', '🚉', '🚊', '🚋', '🚌', '🚍', '🚎', '🚏', '🚐', '🚑', '🚒', '🚓', '🚔', '🚕', '🚖', '🚗', '🚘', '🚙', '🚚', '🚛', '🚜', '🚝', '🚞', '🚟', '🚠', '🚡', '🚢', '🚣', '🚤', '🚥', '🚦', '🚧', '🚨', '🚩', '🚪', '🚫', '🚬', '🚭', '🚮', '🚯', '🚰', '🚱', '🚲', '🚳', '🚴', '🚵', '🚶', '🚷', '🚸', '🚹', '🚺', '🚻', '🚼', '🚽', '🚾', '🚿', '🛀', '🛁', '🛂', '🛃', '🛄', '🛅', '🛌', '🛐', '🛑', '🛒', '🛫', '🛬', '🛴', '🛵', '🛶', '🤐', '🤑', '🤒', '🤓', '🤔', '🤕', '🤖', '🤗', '🤘', '🤙', '🤚', '🤛', '🤜', '🤝', '🤞', '🤠', '🤡', '🤢', '🤣', '🤤', '🤥', '🤦', '🤧', '🤰', '🤳', '🤴', '🤵', '🤶', '🤷', '🤸', '🤹', '🤺', '🤼', '🤽', '🤾', '🥀', '🥁', '🥂', '🥃', '🥄', '🥅', '🥇', '🥈', '🥉', '🥊', '🥋', '🥐', '🥑', '🥒', '🥓', '🥔', '🥕', '🥖', '🥗', '🥘', '🥙', '🥚', '🥛', '🥜', '🥝', '🥞', '🦀', '🦁', '🦂', '🦃', '🦄', '🦅', '🦆', '🦇', '🦈', '🦉', '🦊', '🦋', '🦌', '🦍', '🦎', '🦏', '🦐', '🦑', '🧀', '⌚', '⌛', '⏩', '⏪', '⏫', '⏬', '⏰', '⏳', '◽', '◾', '☔', '☕', '♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓', '♿', '⚓', '⚡', '⚪', '⚫', '⚽', '⚾', '⛄', '⛅', '⛎', '⛔', '⛪', '⛲', '⛳', '⛵', '⛺', '⛽', '✅', '✊', '✋', '✨', '❌', '❎', '❓', '❔', '❕', '❗', '➕', '➖', '➗', '➰', '➿', '⬛', '⬜', '⭐', '⭕']


def slackToZulipDict():
    """
    The output as defined from getCommonEmojis(), copy and pasted to prevent the extra computation that would be required each time an emoji is used in the integration.
    """
    return {':mahjong:': ':mahjong:', ':black_joker:': ':joker:', ':ab:': ':ab:', ':cl:': ':cl:', ':cool:': ':cool:', ':free:': ':free:', ':id:': ':id:', ':new:': ':new:', ':ng:': ':ng:', ':ok:': ':squared_ok:', ':sos:': ':sos:', ':up:': ':squared_up:', ':vs:': ':vs:', ':cyclone:': ':cyclone:', ':foggy:': ':foggy:', ':closed_umbrella:': ':closed_umbrella:', ':night_with_stars:': ':night:', ':sunrise_over_mountains:': ':mountain_sunrise:', ':sunrise:': ':sunrise:', ':city_sunset:': ':sunset:', ':city_sunrise:': ':city_sunrise:', ':rainbow:': ':rainbow:', ':bridge_at_night:': ':bridge:', ':ocean:': ':ocean:', ':volcano:': ':volcano:', ':milky_way:': ':milky_way:', ':earth_africa:': ':earth_africa:', ':earth_americas:': ':earth_americas:', ':earth_asia:': ':earth_asia:', ':globe_with_meridians:': ':www:', ':new_moon:': ':new_moon:', ':moon:': ':waxing_moon:', ':full_moon:': ':full_moon:', ':crescent_moon:': ':moon:', ':new_moon_with_face:': ':new_moon_face:', ':first_quarter_moon_with_face:': ':goodnight:', ':full_moon_with_face:': ':moon_face:', ':sun_with_face:': ':sun_face:', ':star2:': ':glowing_star:', ':stars:': ':shooting_star:', ':hotdog:': ':hotdog:', ':taco:': ':taco:', ':burrito:': ':burrito:', ':chestnut:': ':chestnut:', ':seedling:': ':seedling:', ':evergreen_tree:': ':evergreen_tree:', ':deciduous_tree:': ':tree:', ':palm_tree:': ':palm_tree:', ':cactus:': ':cactus:', ':tulip:': ':tulip:', ':cherry_blossom:': ':cherry_blossom:', ':rose:': ':rose:', ':hibiscus:': ':hibiscus:', ':sunflower:': ':sunflower:', ':blossom:': ':blossom:', ':corn:': ':corn:', ':ear_of_rice:': ':harvest:', ':herb:': ':herb:', ':four_leaf_clover:': ':lucky:', ':maple_leaf:': ':maple_leaf:', ':fallen_leaf:': ':fallen_leaf:', ':leaves:': ':leaves:', ':mushroom:': ':mushroom:', ':tomato:': ':tomato:', ':eggplant:': ':eggplant:', ':grapes:': ':grapes:', ':melon:': ':melon:', ':watermelon:': ':watermelon:', ':tangerine:': ':orange:', ':lemon:': ':lemon:', ':banana:': ':banana:', ':pineapple:': ':pineapple:', ':apple:': ':apple:', ':green_apple:': ':green_apple:', ':pear:': ':pear:', ':peach:': ':peach:', ':cherries:': ':cherries:', ':strawberry:': ':strawberry:', ':hamburger:': ':hamburger:', ':pizza:': ':pizza:', ':meat_on_bone:': ':meat:', ':poultry_leg:': ':drumstick:', ':rice_cracker:': ':senbei:', ':rice_ball:': ':onigiri:', ':rice:': ':rice:', ':curry:': ':curry:', ':ramen:': ':ramen:', ':spaghetti:': ':spaghetti:', ':bread:': ':bread:', ':fries:': ':fries:', ':sweet_potato:': ':yam:', ':dango:': ':dango:', ':oden:': ':oden:', ':sushi:': ':sushi:', ':fried_shrimp:': ':tempura:', ':fish_cake:': ':naruto:', ':icecream:': ':soft_serve:', ':shaved_ice:': ':shaved_ice:', ':ice_cream:': ':ice_cream:', ':doughnut:': ':donut:', ':cookie:': ':cookie:', ':chocolate_bar:': ':chocolate:', ':candy:': ':candy:', ':lollipop:': ':lollipop:', ':custard:': ':custard:', ':honey_pot:': ':honey:', ':cake:': ':cake:', ':bento:': ':bento:', ':stew:': ':food:', ':fried_egg:': ':cooking:', ':fork_and_knife:': ':fork_and_knife:', ':tea:': ':tea:', ':sake:': ':sake:', ':wine_glass:': ':wine:', ':cocktail:': ':cocktail:', ':tropical_drink:': ':tropical_drink:', ':beer:': ':beer:', ':beers:': ':beers:', ':baby_bottle:': ':baby_bottle:', ':champagne:': ':champagne:', ':popcorn:': ':popcorn:', ':ribbon:': ':ribbon:', ':gift:': ':gift:', ':birthday:': ':birthday:', ':jack_o_lantern:': ':jack-o-lantern:', ':christmas_tree:': ':holiday_tree:', ':santa:': ':santa:', ':fireworks:': ':fireworks:', ':sparkler:': ':sparkler:', ':balloon:': ':balloon:', ':tada:': ':tada:', ':confetti_ball:': ':confetti:', ':tanabata_tree:': ':wish_tree:', ':crossed_flags:': ':crossed_flags:', ':bamboo:': ':bamboo:', ':dolls:': ':dolls:', ':flags:': ':carp_streamer:', ':wind_chime:': ':wind_chime:', ':rice_scene:': ':moon_ceremony:', ':school_satchel:': ':backpack:', ':mortar_board:': ':graduate:', ':carousel_horse:': ':carousel:', ':ferris_wheel:': ':ferris_wheel:', ':roller_coaster:': ':roller_coaster:', ':fishing_pole_and_fish:': ':fishing:', ':microphone:': ':microphone:', ':movie_camera:': ':movie_camera:', ':cinema:': ':cinema:', ':headphones:': ':headphones:', ':art:': ':art:', ':tophat:': ':top_hat:', ':circus_tent:': ':circus:', ':ticket:': ':pass:', ':clapper:': ':action:', ':performing_arts:': ':performing_arts:', ':video_game:': ':video_game:', ':dart:': ':direct_hit:', ':slot_machine:': ':slot_machine:', ':8ball:': ':billiards:', ':game_die:': ':dice:', ':bowling:': ':strike:', ':flower_playing_cards:': ':playing_cards:', ':musical_note:': ':music:', ':notes:': ':musical_notes:', ':saxophone:': ':saxophone:', ':guitar:': ':guitar:', ':musical_keyboard:': ':piano:', ':trumpet:': ':trumpet:', ':violin:': ':violin:', ':musical_score:': ':musical_score:', ':running_shirt_with_sash:': ':running_shirt:', ':tennis:': ':tennis:', ':ski:': ':ski:', ':basketball:': ':basketball:', ':checkered_flag:': ':checkered_flag:', ':snowboarder:': ':snowboarder:', ':runner:': ':running:', ':surfer:': ':surf:', ':sports_medal:': ':medal:', ':trophy:': ':trophy:', ':horse_racing:': ':horse_racing:', ':football:': ':american_football:', ':rugby_football:': ':rugby:', ':swimmer:': ':swim:', ':cricket_bat_and_ball:': ':cricket:', ':volleyball:': ':volleyball:', ':field_hockey_stick_and_ball:': ':field_hockey:', ':ice_hockey_stick_and_puck:': ':ice_hockey:', ':table_tennis_paddle_and_ball:': ':ping_pong:', ':house:': ':house:', ':house_with_garden:': ':suburb:', ':office:': ':office:', ':post_office:': ':japan_post:', ':european_post_office:': ':post_office:', ':hospital:': ':hospital:', ':bank:': ':bank:', ':atm:': ':atm:', ':hotel:': ':hotel:', ':love_hotel:': ':love_hotel:', ':convenience_store:': ':convenience_store:', ':school:': ':school:', ':department_store:': ':department_store:', ':factory:': ':factory:', ':izakaya_lantern:': ':lantern:', ':japanese_castle:': ':shiro:', ':european_castle:': ':castle:', ':waving_black_flag:': ':black_flag:', ':badminton_racquet_and_shuttlecock:': ':badminton:', ':bow_and_arrow:': ':bow_and_arrow:', ':amphora:': ':vase:', ':rat:': ':rat:', ':mouse2:': ':mouse:', ':ox:': ':ox:', ':water_buffalo:': ':water_buffalo:', ':cow2:': ':cow:', ':tiger2:': ':tiger:', ':leopard:': ':leopard:', ':rabbit2:': ':rabbit:', ':cat2:': ':cat:', ':dragon:': ':dragon:', ':crocodile:': ':crocodile:', ':whale2:': ':humpback_whale:', ':snail:': ':snail:', ':snake:': ':snake:', ':racehorse:': ':horse:', ':ram:': ':ram:', ':goat:': ':goat:', ':sheep:': ':sheep:', ':monkey:': ':monkey:', ':rooster:': ':rooster:', ':chicken:': ':chicken:', ':dog2:': ':dog:', ':pig2:': ':pig:', ':boar:': ':boar:', ':elephant:': ':elephant:', ':octopus:': ':octopus:', ':shell:': ':shell:', ':bug:': ':bug:', ':ant:': ':ant:', ':bee:': ':bee:', ':ladybug:': ':beetle:', ':fish:': ':fish:', ':tropical_fish:': ':tropical_fish:', ':blowfish:': ':blowfish:', ':turtle:': ':turtle:', ':hatching_chick:': ':hatching:', ':baby_chick:': ':chick:', ':hatched_chick:': ':new_baby:', ':bird:': ':bird:', ':penguin:': ':penguin:', ':koala:': ':koala:', ':poodle:': ':poodle:', ':dromedary_camel:': ':arabian_camel:', ':camel:': ':camel:', ':dolphin:': ':dolphin:', ':mouse:': ':dormouse:', ':cow:': ':calf:', ':tiger:': ':tiger_cub:', ':rabbit:': ':bunny:', ':cat:': ':kitten:', ':dragon_face:': ':dragon_face:', ':whale:': ':whale:', ':horse:': ':pony:', ':monkey_face:': ':monkey_face:', ':dog:': ':puppy:', ':pig:': ':piglet:', ':frog:': ':frog:', ':hamster:': ':hamster:', ':wolf:': ':wolf:', ':bear:': ':bear:', ':panda_face:': ':panda:', ':pig_nose:': ':pig_nose:', ':feet:': ':paw_prints:', ':eyes:': ':eyes:', ':ear:': ':ear:', ':nose:': ':nose:', ':lips:': ':lips:', ':tongue:': ':tongue:', ':point_up_2:': ':point_up:', ':point_down:': ':point_down:', ':point_left:': ':point_left:', ':point_right:': ':point_right:', ':facepunch:': ':fist_bump:', ':wave:': ':wave:', ':ok_hand:': ':ok:', ':+1:': ':+1:', ':-1:': ':-1:', ':clap:': ':clap:', ':open_hands:': ':open_hands:', ':crown:': ':crown:', ':womans_hat:': ':hat:', ':eyeglasses:': ':glasses:', ':necktie:': ':tie:', ':shirt:': ':shirt:', ':jeans:': ':jeans:', ':dress:': ':dress:', ':kimono:': ':kimono:', ':bikini:': ':bikini:', ':womans_clothes:': ':clothing:', ':purse:': ':purse:', ':handbag:': ':handbag:', ':pouch:': ':pouch:', ':mans_shoe:': ':shoe:', ':athletic_shoe:': ':athletic_shoe:', ':high_heel:': ':high_heels:', ':sandal:': ':sandal:', ':boot:': ':boot:', ':footprints:': ':footprints:', ':bust_in_silhouette:': ':silhouette:', ':busts_in_silhouette:': ':silhouettes:', ':boy:': ':boy:', ':girl:': ':girl:', ':man:': ':man:', ':woman:': ':woman:', ':family:': ':family:', ':man_and_woman_holding_hands:': ':man_and_woman_holding_hands:', ':two_men_holding_hands:': ':two_men_holding_hands:', ':two_women_holding_hands:': ':two_women_holding_hands:', ':cop:': ':police:', ':dancers:': ':dancers:', ':bride_with_veil:': ':bride:', ':man_with_gua_pi_mao:': ':gua_pi_mao:', ':man_with_turban:': ':turban:', ':older_man:': ':older_man:', ':older_woman:': ':older_woman:', ':baby:': ':baby:', ':construction_worker:': ':construction_worker:', ':princess:': ':princess:', ':japanese_ogre:': ':ogre:', ':japanese_goblin:': ':goblin:', ':ghost:': ':ghost:', ':angel:': ':angel:', ':alien:': ':alien:', ':space_invader:': ':space_invader:', ':imp:': ':devil:', ':skull:': ':skull:', ':information_desk_person:': ':information_desk_person:', ':guardsman:': ':guard:', ':dancer:': ':dancer:', ':lipstick:': ':lipstick:', ':nail_care:': ':nail_polish:', ':massage:': ':massage:', ':haircut:': ':haircut:', ':barber:': ':barber:', ':syringe:': ':injection:', ':pill:': ':medicine:', ':kiss:': ':lipstick_kiss:', ':love_letter:': ':love_letter:', ':ring:': ':ring:', ':gem:': ':gem:', ':bouquet:': ':bouquet:', ':wedding:': ':wedding:', ':heartbeat:': ':heartbeat:', ':broken_heart:': ':broken_heart:', ':two_hearts:': ':two_hearts:', ':sparkling_heart:': ':sparkling_heart:', ':heartpulse:': ':heart_pulse:', ':cupid:': ':cupid:', ':blue_heart:': ':blue_heart:', ':green_heart:': ':green_heart:', ':yellow_heart:': ':yellow_heart:', ':purple_heart:': ':purple_heart:', ':gift_heart:': ':gift_heart:', ':revolving_hearts:': ':revolving_hearts:', ':heart_decoration:': ':heart_box:', ':diamond_shape_with_a_dot_inside:': ':cute:', ':bulb:': ':light_bulb:', ':anger:': ':anger:', ':bomb:': ':bomb:', ':zzz:': ':zzz:', ':boom:': ':boom:', ':sweat_drops:': ':sweat_drops:', ':droplet:': ':drop:', ':dash:': ':dash:', ':hankey:': ':poop:', ':muscle:': ':muscle:', ':dizzy:': ':seeing_stars:', ':speech_balloon:': ':umm:', ':thought_balloon:': ':thought:', ':white_flower:': ':white_flower:', ':100:': ':100:', ':moneybag:': ':money:', ':currency_exchange:': ':exchange:', ':heavy_dollar_sign:': ':dollars:', ':credit_card:': ':credit_card:', ':yen:': ':yen_banknotes:', ':dollar:': ':dollar_bills:', ':euro:': ':euro_banknotes:', ':pound:': ':pound_notes:', ':money_with_wings:': ':losing_money:', ':chart:': ':stock_market:', ':seat:': ':seat:', ':computer:': ':computer:', ':briefcase:': ':briefcase:', ':minidisc:': ':gold_record:', ':floppy_disk:': ':floppy_disk:', ':cd:': ':cd:', ':dvd:': ':dvd:', ':file_folder:': ':organize:', ':open_file_folder:': ':folder:', ':page_with_curl:': ':receipt:', ':page_facing_up:': ':document:', ':date:': ':calendar:', ':calendar:': ':date:', ':card_index:': ':rolodex:', ':chart_with_upwards_trend:': ':chart:', ':chart_with_downwards_trend:': ':downwards_trend:', ':bar_chart:': ':bar_chart:', ':clipboard:': ':clipboard:', ':pushpin:': ':push_pin:', ':round_pushpin:': ':pin:', ':paperclip:': ':paperclip:', ':straight_ruler:': ':ruler:', ':triangular_ruler:': ':carpenter_square:', ':bookmark_tabs:': ':place_holder:', ':ledger:': ':ledger:', ':notebook:': ':notebook:', ':notebook_with_decorative_cover:': ':decorative_notebook:', ':closed_book:': ':red_book:', ':book:': ':book:', ':green_book:': ':green_book:', ':blue_book:': ':blue_book:', ':orange_book:': ':orange_book:', ':books:': ':books:', ':name_badge:': ':name_badge:', ':scroll:': ':scroll:', ':memo:': ':memo:', ':telephone_receiver:': ':landline:', ':pager:': ':pager:', ':fax:': ':fax:', ':satellite_antenna:': ':satellite_antenna:', ':loudspeaker:': ':loudspeaker:', ':mega:': ':megaphone:', ':outbox_tray:': ':outbox:', ':inbox_tray:': ':inbox:', ':package:': ':package:', ':e-mail:': ':e-mail:', ':incoming_envelope:': ':mail_received:', ':envelope_with_arrow:': ':mail_sent:', ':mailbox_closed:': ':closed_mailbox:', ':mailbox:': ':mailbox:', ':mailbox_with_mail:': ':unread_mail:', ':mailbox_with_no_mail:': ':inbox_zero:', ':postbox:': ':mail_dropoff:', ':postal_horn:': ':horn:', ':newspaper:': ':headlines:', ':iphone:': ':mobile_phone:', ':calling:': ':calling:', ':vibration_mode:': ':vibration_mode:', ':mobile_phone_off:': ':phone_off:', ':no_mobile_phones:': ':no_phones:', ':signal_strength:': ':cell_reception:', ':camera:': ':camera:', ':camera_with_flash:': ':taking_a_picture:', ':video_camera:': ':video_camera:', ':tv:': ':tv:', ':radio:': ':radio:', ':vhs:': ':vhs:', ':prayer_beads:': ':prayer_beads:', ':twisted_rightwards_arrows:': ':shuffle:', ':repeat:': ':repeat:', ':repeat_one:': ':repeat_one:', ':arrows_clockwise:': ':clockwise:', ':arrows_counterclockwise:': ':counterclockwise:', ':low_brightness:': ':low_brightness:', ':high_brightness:': ':brightness:', ':mute:': ':mute:', ':speaker:': ':speaker:', ':sound:': ':softer:', ':loud_sound:': ':louder:', ':battery:': ':battery:', ':electric_plug:': ':electric_plug:', ':mag:': ':search:', ':lock_with_ink_pen:': ':privacy:', ':closed_lock_with_key:': ':secure:', ':key:': ':key:', ':lock:': ':locked:', ':unlock:': ':unlocked:', ':bell:': ':notifications:', ':no_bell:': ':mute_notifications:', ':bookmark:': ':bookmark:', ':link:': ':link:', ':radio_button:': ':radio_button:', ':back:': ':back:', ':end:': ':end:', ':on:': ':on:', ':soon:': ':soon:', ':top:': ':top:', ':underage:': ':underage:', ':keycap_ten:': ':ten:', ':capital_abcd:': ':capital_abcd:', ':abcd:': ':abcd:', ':1234:': ':1234:', ':symbols:': ':symbols:', ':abc:': ':abc:', ':fire:': ':fire:', ':flashlight:': ':flashlight:', ':wrench:': ':fixing:', ':hammer:': ':hammer:', ':nut_and_bolt:': ':nut_and_bolt:', ':hocho:': ':knife:', ':gun:': ':gun:', ':microscope:': ':science:', ':telescope:': ':telescope:', ':crystal_ball:': ':crystal_ball:', ':beginner:': ':beginner:', ':trident:': ':trident:', ':black_square_button:': ':white_and_black_square:', ':white_square_button:': ':black_and_white_square:', ':red_circle:': ':red_circle:', ':large_blue_circle:': ':blue_circle:', ':large_orange_diamond:': ':large_orange_diamond:', ':large_blue_diamond:': ':large_blue_diamond:', ':small_orange_diamond:': ':small_orange_diamond:', ':small_blue_diamond:': ':small_blue_diamond:', ':small_red_triangle:': ':red_triangle_up:', ':small_red_triangle_down:': ':red_triangle_down:', ':arrow_up_small:': ':upvote:', ':arrow_down_small:': ':downvote:', ':kaaba:': ':kaaba:', ':mosque:': ':mosque:', ':synagogue:': ':synagogue:', ':menorah_with_nine_branches:': ':menorah:', ':clock8:': ':time:', ':man_dancing:': ':dancing:', ':middle_finger:': ':middle_finger:', ':spock-hand:': ':spock:', ':black_heart:': ':black_heart:', ':mount_fuji:': ':mount_fuji:', ':tokyo_tower:': ':tower:', ':statue_of_liberty:': ':statue:', ':japan:': ':japan:', ':moyai:': ':rock_carving:', ':grinning:': ':grinning:', ':grin:': ':grinning_face_with_smiling_eyes:', ':joy:': ':joy:', ':smiley:': ':smiley:', ':smile:': ':big_smile:', ':sweat_smile:': ':sweat_smile:', ':laughing:': ':laughing:', ':innocent:': ':innocent:', ':smiling_imp:': ':smiling_devil:', ':wink:': ':wink:', ':blush:': ':blush:', ':yum:': ':yum:', ':relieved:': ':relieved:', ':heart_eyes:': ':heart_eyes:', ':sunglasses:': ':sunglasses:', ':smirk:': ':smirk:', ':neutral_face:': ':neutral:', ':expressionless:': ':expressionless:', ':unamused:': ':unamused:', ':sweat:': ':sweat:', ':pensive:': ':pensive:', ':confused:': ':oh_no:', ':confounded:': ':confounded:', ':kissing:': ':kiss:', ':kissing_heart:': ':heart_kiss:', ':kissing_smiling_eyes:': ':kiss_smiling_eyes:', ':kissing_closed_eyes:': ':kiss_with_blush:', ':stuck_out_tongue:': ':stuck_out_tongue:', ':stuck_out_tongue_winking_eye:': ':stuck_out_tongue_wink:', ':stuck_out_tongue_closed_eyes:': ':stuck_out_tongue_closed_eyes:', ':disappointed:': ':disappointed:', ':worried:': ':worried:', ':angry:': ':angry:', ':rage:': ':rage:', ':cry:': ':cry:', ':persevere:': ':persevere:', ':triumph:': ':triumph:', ':disappointed_relieved:': ':exhausted:', ':frowning:': ':frowning:', ':anguished:': ':anguished:', ':fearful:': ':fear:', ':weary:': ':weary:', ':sleepy:': ':sleepy:', ':tired_face:': ':anguish:', ':grimacing:': ':grimacing:', ':sob:': ':sob:', ':open_mouth:': ':open_mouth:', ':hushed:': ':hushed:', ':cold_sweat:': ':cold_sweat:', ':scream:': ':scream:', ':astonished:': ':astonished:', ':flushed:': ':flushed:', ':sleeping:': ':sleeping:', ':dizzy_face:': ':dizzy:', ':no_mouth:': ':speechless:', ':mask:': ':cant_talk:', ':smile_cat:': ':smile_cat:', ':joy_cat:': ':joy_cat:', ':smiley_cat:': ':smiley_cat:', ':heart_eyes_cat:': ':heart_eyes_cat:', ':smirk_cat:': ':smirk_cat:', ':kissing_cat:': ':kissing_cat:', ':pouting_cat:': ':angry_cat:', ':crying_cat_face:': ':crying_cat:', ':scream_cat:': ':scream_cat:', ':slightly_frowning_face:': ':frown:', ':slightly_smiling_face:': ':smile:', ':upside_down_face:': ':upside_down:', ':face_with_rolling_eyes:': ':rolling_eyes:', ':no_good:': ':no_signal:', ':ok_woman:': ':ok_signal:', ':bow:': ':bow:', ':see_no_evil:': ':see_no_evil:', ':hear_no_evil:': ':hear_no_evil:', ':speak_no_evil:': ':speak_no_evil:', ':raising_hand:': ':raising_hand:', ':raised_hands:': ':raised_hands:', ':person_frowning:': ':person_frowning:', ':person_with_pouting_face:': ':person_pouting:', ':pray:': ':pray:', ':rocket:': ':rocket:', ':helicopter:': ':helicopter:', ':steam_locomotive:': ':train:', ':railway_car:': ':railway_car:', ':bullettrain_side:': ':high_speed_train:', ':bullettrain_front:': ':bullet_train:', ':train2:': ':oncoming_train:', ':metro:': ':subway:', ':light_rail:': ':light_rail:', ':station:': ':station:', ':tram:': ':oncoming_tram:', ':train:': ':tram:', ':bus:': ':bus:', ':oncoming_bus:': ':oncoming_bus:', ':trolleybus:': ':trolley:', ':busstop:': ':bus_stop:', ':minibus:': ':minibus:', ':ambulance:': ':ambulance:', ':fire_engine:': ':fire_truck:', ':police_car:': ':police_car:', ':oncoming_police_car:': ':oncoming_police_car:', ':taxi:': ':taxi:', ':oncoming_taxi:': ':oncoming_taxi:', ':car:': ':car:', ':oncoming_automobile:': ':oncoming_car:', ':blue_car:': ':recreational_vehicle:', ':truck:': ':moving_truck:', ':articulated_lorry:': ':truck:', ':tractor:': ':tractor:', ':monorail:': ':monorail:', ':mountain_railway:': ':mountain_railway:', ':suspension_railway:': ':suspension_railway:', ':mountain_cableway:': ':gondola:', ':aerial_tramway:': ':aerial_tramway:', ':ship:': ':ship:', ':rowboat:': ':rowboat:', ':speedboat:': ':speedboat:', ':traffic_light:': ':horizontal_traffic_light:', ':vertical_traffic_light:': ':traffic_light:', ':construction:': ':work_in_progress:', ':rotating_light:': ':siren:', ':triangular_flag_on_post:': ':triangular_flag:', ':door:': ':door:', ':no_entry_sign:': ':prohibited:', ':smoking:': ':smoking:', ':no_smoking:': ':no_smoking:', ':put_litter_in_its_place:': ':put_litter_in_its_place:', ':do_not_litter:': ':do_not_litter:', ':potable_water:': ':potable_water:', ':non-potable_water:': ':non-potable_water:', ':bike:': ':bike:', ':no_bicycles:': ':no_bicycles:', ':bicyclist:': ':cyclist:', ':mountain_bicyclist:': ':mountain_biker:', ':walking:': ':walking:', ':no_pedestrians:': ':no_pedestrians:', ':children_crossing:': ':children_crossing:', ':mens:': ':mens:', ':womens:': ':womens:', ':restroom:': ':restroom:', ':baby_symbol:': ':baby_change_station:', ':toilet:': ':toilet:', ':wc:': ':wc:', ':shower:': ':shower:', ':bath:': ':bath:', ':bathtub:': ':bathtub:', ':passport_control:': ':passport_control:', ':customs:': ':customs:', ':baggage_claim:': ':baggage_claim:', ':left_luggage:': ':locker:', ':sleeping_accommodation:': ':in_bed:', ':place_of_worship:': ':place_of_worship:', ':octagonal_sign:': ':stop_sign:', ':shopping_trolley:': ':shopping_cart:', ':airplane_departure:': ':take_off:', ':airplane_arriving:': ':landing:', ':scooter:': ':kick_scooter:', ':motor_scooter:': ':scooter:', ':canoe:': ':canoe:', ':zipper_mouth_face:': ':silence:', ':money_mouth_face:': ':money_face:', ':face_with_thermometer:': ':sick:', ':nerd_face:': ':nerd:', ':thinking_face:': ':thinking:', ':face_with_head_bandage:': ':hurt:', ':robot_face:': ':robot:', ':hugging_face:': ':hug:', ':the_horns:': ':rock_on:', ':call_me_hand:': ':call_me:', ':raised_back_of_hand:': ':stop:', ':left-facing_fist:': ':left_fist:', ':right-facing_fist:': ':right_fist:', ':handshake:': ':handshake:', ':crossed_fingers:': ':fingers_crossed:', ':face_with_cowboy_hat:': ':cowboy:', ':clown_face:': ':clown:', ':nauseated_face:': ':nauseated:', ':rolling_on_the_floor_laughing:': ':rolling_on_the_floor_laughing:', ':drooling_face:': ':drooling:', ':lying_face:': ':lying:', ':face_palm:': ':face_palm:', ':sneezing_face:': ':sneezing:', ':pregnant_woman:': ':pregnant:', ':selfie:': ':selfie:', ':prince:': ':prince:', ':person_in_tuxedo:': ':tuxedo:', ':mrs_claus:': ':mother_christmas:', ':shrug:': ':shrug:', ':person_doing_cartwheel:': ':cartwheel:', ':juggling:': ':juggling:', ':fencer:': ':fencing:', ':wrestlers:': ':wrestling:', ':water_polo:': ':water_polo:', ':handball:': ':handball:', ':wilted_flower:': ':wilted_flower:', ':drum_with_drumsticks:': ':drum:', ':clinking_glasses:': ':clink:', ':tumbler_glass:': ':small_glass:', ':spoon:': ':spoon:', ':goal_net:': ':gooooooooal:', ':first_place_medal:': ':first_place:', ':second_place_medal:': ':second_place:', ':third_place_medal:': ':third_place:', ':boxing_glove:': ':boxing_glove:', ':martial_arts_uniform:': ':black_belt:', ':croissant:': ':croissant:', ':avocado:': ':avocado:', ':cucumber:': ':cucumber:', ':bacon:': ':bacon:', ':potato:': ':potato:', ':carrot:': ':carrot:', ':baguette_bread:': ':baguette:', ':green_salad:': ':salad:', ':shallow_pan_of_food:': ':paella:', ':stuffed_flatbread:': ':doner_kebab:', ':egg:': ':egg:', ':glass_of_milk:': ':milk:', ':peanuts:': ':peanuts:', ':kiwifruit:': ':kiwi:', ':pancakes:': ':pancakes:', ':crab:': ':crab:', ':lion_face:': ':lion:', ':scorpion:': ':scorpion:', ':turkey:': ':turkey:', ':unicorn_face:': ':unicorn:', ':eagle:': ':eagle:', ':duck:': ':duck:', ':bat:': ':bat:', ':shark:': ':shark:', ':owl:': ':owl:', ':fox_face:': ':fox:', ':butterfly:': ':butterfly:', ':deer:': ':deer:', ':gorilla:': ':gorilla:', ':lizard:': ':lizard:', ':rhinoceros:': ':rhinoceros:', ':shrimp:': ':shrimp:', ':squid:': ':squid:', ':cheese_wedge:': ':cheese:', ':watch:': ':watch:', ':hourglass:': ':times_up:', ':fast_forward:': ':fast_forward:', ':rewind:': ':rewind:', ':arrow_double_up:': ':double_up:', ':arrow_double_down:': ':double_down:', ':alarm_clock:': ':alarm_clock:', ':hourglass_flowing_sand:': ':time_ticking:', ':white_medium_small_square:': ':white_medium_small_square:', ':black_medium_small_square:': ':black_medium_small_square:', ':umbrella_with_rain_drops:': ':umbrella_with_rain:', ':coffee:': ':coffee:', ':aries:': ':aries:', ':taurus:': ':taurus:', ':gemini:': ':gemini:', ':cancer:': ':cancer:', ':leo:': ':leo:', ':virgo:': ':virgo:', ':libra:': ':libra:', ':scorpius:': ':scorpius:', ':sagittarius:': ':sagittarius:', ':capricorn:': ':capricorn:', ':aquarius:': ':aquarius:', ':pisces:': ':pisces:', ':wheelchair:': ':accessible:', ':anchor:': ':anchor:', ':zap:': ':high_voltage:', ':white_circle:': ':white_circle:', ':black_circle:': ':black_circle:', ':soccer:': ':football:', ':baseball:': ':baseball:', ':snowman_without_snow:': ':frosty:', ':partly_sunny:': ':partly_sunny:', ':ophiuchus:': ':ophiuchus:', ':no_entry:': ':no_entry:', ':church:': ':church:', ':fountain:': ':fountain:', ':golf:': ':hole_in_one:', ':boat:': ':boat:', ':tent:': ':tent:', ':fuelpump:': ':fuel_pump:', ':white_check_mark:': ':check:', ':fist:': ':fist:', ':hand:': ':hand:', ':sparkles:': ':sparkles:', ':x:': ':cross_mark:', ':negative_squared_cross_mark:': ':x:', ':question:': ':question:', ':grey_question:': ':grey_question:', ':grey_exclamation:': ':grey_exclamation:', ':exclamation:': ':exclamation:', ':heavy_plus_sign:': ':plus:', ':heavy_minus_sign:': ':minus:', ':heavy_division_sign:': ':division:', ':curly_loop:': ':loop:', ':loop:': ':double_loop:', ':black_large_square:': ':black_large_square:', ':white_large_square:': ':white_large_square:', ':star:': ':star:', ':o:': ':circle:'}


def zulipToSlackDict():
    """
    Swaps the slackToZulipDict() output, for messages coming from Zulip to Slack.
    """
    return {value:key for key, value in slackToZulipDict().items()}