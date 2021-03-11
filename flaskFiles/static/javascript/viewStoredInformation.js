function onmouseOn(id, value) {
    // reveal the sensitive data on mouse over
    document.getElementById(id).value = value;
}

function onmouseOff(id) {
    // hide the information when the cursor is not on the field
    document.getElementById(id).value = "*************";
}