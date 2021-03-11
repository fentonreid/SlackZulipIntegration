function setUploadAttributes(id, token) {
    // depending on the token state display a bootstrap button with certain text
    if (token === 'NONE') {
        document.getElementById(id).className = "btn btn-info btn-sm";
        document.getElementById(id).innerHTML = "Setup";
    } else {
        document.getElementById(id).className = "btn btn-success btn-sm";
        document.getElementById(id).innerHTML = "Done";
    }
}

function setValidateAttributes(id, token, tokenValidity) {
    if (token === 'NONE') {
        // change button title, colour and style
        document.getElementById(id).value = "Upload first";
        document.getElementById(id).className = "btn btn-danger btn-sm";
        document.getElementById(id).style = "pointer-events: none;";
    } else {
        // check the current validity of the button
        switch (tokenValidity) {
            case 'Not Checked':
                document.getElementById(id).className = "btn btn-warning btn-sm";
                break;

            case 'Invalid':
                document.getElementById(id).className = "btn btn-danger btn-sm";
                break;

            case 'Incomplete':
                document.getElementById(id).className = "btn btn-secondary btn-sm";
                break;

            case 'Valid':
                document.getElementById(id).className = "btn btn-success btn-sm";
                break;

            default:
                document.getElementById(id).className = "btn btn-danger btn-sm";
        }
    }
}