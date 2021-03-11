function showSpinner() {
    // show spinner and disable post button
    document.getElementById("loadingSpinner").style.display = "inherit";
    document.getElementById("runTestButton").disabled = true;
}

function toggleButton() {
    // enable or disable the run tests button depending on the accept checkbox state
    if (document.getElementById("acceptBox").checked) {
        document.getElementById("runTestButton").disabled = false;
    } else {
        document.getElementById("runTestButton").disabled = true;
    }
}