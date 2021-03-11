// setting up variables
let socket = null;
let queue_id = null;
let lastEventID = -1;
let controller = new AbortController();


function alterTooltipMessage(id, message) {
    // jQuery code to alter the tooltip message after its initialisation
    $(id).attr('data-original-title', message);
}

function registerZulipQueue() {
    // call the flask \api\registerQueue endpoint
    return fetch("\\api\\registerQueue", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(zulipRegister => {
            // if the response is valid continue to startZulip
            if ('queue_id' in zulipRegister) {
                queue_id = zulipRegister['queue_id'];
                startZulip();
            } else {
                throw Error('Failed to fetch from /api/v1/register')
            }
        })
        .catch(e => {
            document.getElementById('zulipState').innerHTML = "<b>COULD NOT REGISTER QUEUE</b>";
            document.getElementById('zulipStatus').src = "/static/images/redCircle.png";

            alterTooltipMessage(zulipStatus, e.toString());
        })
    }


function registerSlackSocket() {
    // call the flask \api\registerSocket endpoint
    return fetch("\\api\\registerSocket", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(slackSocket => {
            // if the response is valid continue to startSlack
            if ('socketURL' in slackSocket) {
                socket = new WebSocket(slackSocket['socketURL']);
                startSlack();
            } else {
                throw Error('Failed to fetch from https://slack.com/api/apps.connections.open')
            }
        })
        .catch(e => {
            document.getElementById('slackState').innerHTML = "<b>COULD NOT REGISTER SOCKET</b>";
            document.getElementById('slackStatus').src = "/static/images/redCircle.png";

            alterTooltipMessage(slackStatus, e.toString());
        })
}

function startIntegration() {
    // change the page properties
    document.getElementById("startButton").disabled = true;
    document.getElementById("stopButton").disabled = false;

    // setting up variables
    socket = null;
    queue_id = null;
    lastEventID = -1;
    controller = new AbortController();

    // begin to setup the integration
    registerZulipQueue();
    registerSlackSocket();
}

function safeStop() {
    // change the page properties
    document.getElementById("startButton").disabled = false;
    document.getElementById("stopButton").disabled = true;

    document.getElementById('slackStatus').src = "/static/images/redCircle.png";
    document.getElementById('zulipStatus').src = "/static/images/redCircle.png";

}


function stopIntegration() {
    // graphical changes to the page
    document.getElementById('slackState').innerHTML = "<b>CLOSED</b>";
    document.getElementById('zulipState').innerHTML = "<b>CLOSED</b>";

    // closing Slack webSocket
    socket.close();

    // closing Zulip Fetch request
    controller.abort()
}


function startSlack() {
    // open the slack socket
    socket.onopen = e => {
        document.getElementById('slackState').innerHTML = "<b>RECEIVING</b>";
        document.getElementById('slackStatus').src = "/static/images/greenCircle.png";
        alterTooltipMessage(slackStatus, 'Receiving data');
    }

    socket.onmessage = event => {
        // whenever a message is received, parse the stringified result into a JSON format
        let eventJSON = JSON.parse(event.data);

        // send acknowledgement back to Slack, a requirement of Socket Mode
        if ('envelope_id' in eventJSON) {
            socket.send(JSON.stringify({
                "envelope_id": eventJSON['envelope_id']
            }));

            // send to the flask \slackEvents endpoint
            if ('payload' in eventJSON && 'event' in eventJSON['payload'] && eventJSON['retry_attempt'] <= 0) {
                return fetch("\\api\\slackEvents", {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(eventJSON['payload'])
                    })
                    .catch(e => {
                        document.getElementById('slackState').innerHTML = "<b>CLOSED BY EXCEPTION</b>";
                        document.getElementById('slackStatus').src = "/static/images/redCircle.png";
                        alterTooltipMessage(slackStatus, e.toString());
                    })
            }
        } else {
            return "missing envelope_id";
        }
    }

    // on close of the function
    socket.onclose = event => {
        document.getElementById('slackState').innerHTML = "<b>CLOSED</b>";
        document.getElementById('slackStatus').src = "/static/images/redCircle.png";

        alterTooltipMessage(slackStatus, 'Closed by user');

        // change the page properties
        document.getElementById("startButton").disabled = false;
        document.getElementById("stopButton").disabled = true;

        // stop the integration
        safeStop();
        controller.abort();
    };
}


function startZulip() {
    document.getElementById('zulipState').innerHTML = "<b>RECEIVING</b>";
    document.getElementById('zulipStatus').src = "/static/images/greenCircle.png";

    alterTooltipMessage(zulipStatus, 'Receiving data');

    // create url parameters to add to the request
    let latestEvent = new URLSearchParams({
        "queue_id": queue_id,
        "last_event_id": lastEventID
    });


    // fetch the latest event from Zulip
    return fetch(zulipAuth.site + '/api/v1/events?' + latestEvent.toString(), {
            headers: {
                'Authorization': 'Basic ' + btoa(zulipAuth.email + ':' + zulipAuth.key)
            },
            method: 'GET',
            // keeps the fetch alive, if an error occurs in Slack this will be aborted
            signal: controller.signal,
        })
        .then(response => response.json())
        .then(zulipData => {
            // if the request is of the correct format
            if ('result' in zulipData && zulipData.result == 'success' && 'events' in zulipData && 'type' in zulipData.events[0] && zulipData.events[0].type !== 'presence' && zulipData.events[0].type !== 'heartbeat') {
                // pass this fetch to the flask \api\zulipEvents endpoint for further processing
                return fetch("\\api\\zulipEvents", {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        signal: controller.signal,
                        body: JSON.stringify(zulipData)
                    })
                    .then(zulipEndpointData => {
                        // increment the lastEventID so that the last event is ignored, otherwise, recursion will occur
                        if (zulipEndpointData.status === 200) {
                            lastEventID++;
                            // call the function again, this will continue until the signal is aborted
                            startZulip();
                        }
                    })
            } else if('result' in zulipData && zulipData.result == 'success' && 'events' in zulipData && 'type' in zulipData.events[0] && (zulipData.events[0].type === 'presence' || zulipData.events[0].type === 'heartbeat')) {
                lastEventID++;
                startZulip();
            } else {
                // something unknown went wrong did not catch so call again.
                startZulip();
            }
        })
        .catch(e => {
            if (e.name === 'AbortError') {
                document.getElementById('zulipState').innerHTML = "<b>CLOSED</b>";
                alterTooltipMessage(zulipStatus, 'Closed by user');
            } else {
                document.getElementById('zulipState').innerHTML = "<b>CLOSED BY EXCEPTION</b>";
                alterTooltipMessage(zulipStatus, e.toString());
            }

            document.getElementById('zulipStatus').src = "/static/images/redCircle.png";

            safeStop();
            socket.close();
        })
}
