let emojiList = emojiString.split(",");

function fixSpacing() {
    // format the dropdown values to ensure that the spacing between numbers and emojis is consistent
    for (let i = 0; i <= document.getElementById('emojiDropdown').length - 1; i++) {
        let spacing = 4 - (((i + 1).toString()).length);
        let varyingSpacing = '';
        // depending on the length of the field add a varying amount of space
        if (spacing === 2) {
            varyingSpacing = '&nbsp;&nbsp;';
        } else if (spacing === 3) {
            varyingSpacing = '&nbsp;&nbsp;&nbsp;&nbsp;';
        }
        // update the emojiDropdown with the new spacing and define final value
        document.getElementById('emojiDropdown').item(i).innerHTML = (i + 1) + varyingSpacing + emojiList[i];
    }
}

function displayFormatting(input, out) {
    // replace the variables in the input field with example values and display to the output fields
    let inputText = document.getElementById(input).value;
    inputText = inputText.replaceAll('{name}', 'Fenton Reid').replaceAll('{email}', 'fenton@reid.com').replaceAll('{channel}', 'meetings')
    inputText = parseEmojis(inputText.match(/{emoji-\d{1,3}}/g), inputText);

    document.getElementById(out).innerHTML = inputText;
}


function processFormInputs(input, output) {
    // replace any emoji shortcodes with actual values, leave the other variables for processing with correct values
    let formData = document.getElementById(input).value;
    formData = parseEmojis(formData.match(/{emoji-\d{1,3}}/g), formData);
    document.getElementById(output).value = formData;
}


function parseEmojis(emojis, inputText) {
    if (emojis === null) {
        return inputText;
    }
    // convert the short code emoji to actual emoji value based on the emojiList
    let emojiMap = emojis.map(emoji => {
        //convert: {emoji-zzz} to zzz
        numStart = emoji.indexOf('-');
        numEnd = emoji.indexOf('}');

        number = emoji.slice(numStart + 1, numEnd);
        if (number >= 1 && number <= 832) {
            inputText = inputText.replace(emoji, emojiList[number - 1]);
        }
    });

    return inputText;
}

function defaultValues() {
    // set input and output fields to there default values
    document.getElementById('slackInput').value = '{name} from Zulip |';
    document.getElementById('zulipInput').value = '{name} from Slack |';

    displayFormatting('slackInput', 'slackOutput');
    displayFormatting('zulipInput', 'zulipOutput');
}