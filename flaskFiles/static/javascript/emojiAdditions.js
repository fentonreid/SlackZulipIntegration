function addMapping() {
    // ensure it is of the correct emoji format
    if (document.getElementById('addSlack').value.match(/^:[a-zA-Z\_\-]+:$/) !== null && document.getElementById('addZulip').value.match(/^:[a-zA-Z\_\-]+:$/) !== null) {
        document.getElementById('addSlack').style.backgroundColor = "white";
        document.getElementById('addZulip').style.backgroundColor = "white";
        return true;
    } else {
        if (document.getElementById('addSlack').value.match(/^:[a-zA-Z\_\-]+:$/) === null) {
            document.getElementById('addSlack').style.backgroundColor = "red";
        }

        if (document.getElementById('addZulip').value.match(/^:[a-zA-Z\_\-]+:$/) === null) {
            document.getElementById('addZulip').style.backgroundColor = "red";
        }

        return false;
    }
}