// Import jQuery to help with events
let jQueryImport = document.createElement('script');
jQueryImport.src = "https://code.jquery.com/jquery-3.5.1.slim.min.js";
document.head.appendChild(jQueryImport);


/* Edit Prefixes Tests */
describe("Edit Prefixes Testing", () => {
    beforeEach(() => {
        // create an emojiDropdown
        let emojiDropdown = document.createElement("select");
        emojiDropdown.id = "emojiDropdown";

        // create a dropdown item for each emoji in emojiList, the dropdown will be empty until filled by function
        let emojiItems = emojiList.forEach(emoji => emojiDropdown.appendChild(document.createElement('option')));

        // create slackInput and zulipInput
        let slackInput = document.createElement('input');
        slackInput.id = "slackInput";
        slackInput.setAttribute("oninput", "displayFormatting('slackInput', 'slackOutput')");

        let zulipInput = document.createElement('input');
        zulipInput.id = "zulipInput";
        zulipInput.setAttribute("oninput", "displayFormatting('zulipInput', 'zulipOutput')");

        // create slackOutput and zulipOutput
        let slackOutput = document.createElement('label');
        slackOutput.id = "slackOutput";

        let zulipOutput = document.createElement('label');
        zulipOutput.id = "zulipOutput";

        // create form
        let form = document.createElement('form');
        form.id = "form";
        form.setAttribute("onsubmit", "processFormInputs('slackInput', 'slackHidden') & processFormInputs('zulipInput', 'zulipHidden') & event.preventDefault()");

        // create hidden output fields
        let slackHidden = document.createElement('input');
        slackHidden.id = "slackHidden";
        slackHidden.type = "hidden";

        let zulipHidden = document.createElement('input');
        zulipHidden.id = "zulipHidden";
        zulipHidden.type = "hidden";

        // create save button
        let save = document.createElement('button');
        save.id = "save";
        save.type = "submit";

        // create reset to default button
        let resetToDefault = document.createElement('button');
        resetToDefault.id = "resetToDefault";
        resetToDefault.type = "button";
        resetToDefault.setAttribute("onClick", "defaultValues()");

        // add children to form
        form.appendChild(slackHidden);
        form.appendChild(zulipHidden);
        form.appendChild(save);
        form.appendChild(resetToDefault);

        // add elements to the DOM
        document.body.appendChild(emojiDropdown);
        document.body.appendChild(slackInput);
        document.body.appendChild(slackOutput);
        document.body.appendChild(zulipInput);
        document.body.appendChild(zulipOutput);
        document.body.appendChild(form);
    })

    afterEach(() => {
        // remove all dom items defined previously
        ['emojiDropdown', 'slackInput', 'slackOutput', 'zulipInput', 'zulipOutput', 'form'].forEach(e => document.getElementById(e).remove());
    });


    it("Empty dropdown with correct length of items", () => {
        let dropdown = document.getElementById('emojiDropdown');
        expect(dropdown.length).toBe(emojiList.length);
    });

    it("EmojiList is not empty", () => {
        expect(emojiList.length).toBeGreaterThanOrEqual(1);
    });


    it("Emoji dropdown innerHTML", () => {
        fixSpacing();
        //for each emoji ensure the correct number and emoji is displayed
        for (let i = 0; i <= document.getElementById('emojiDropdown').length - 1; i++) {
            expect(document.getElementById('emojiDropdown').item(i).innerHTML.replaceAll('&nbsp;', '')).toEqual((i + 1) + emojiList[i]);
        }
    });


    it("No emojis in input", () => {
        fixSpacing();
        let result = parseEmojis(null, 'no emojis in this prefix');
        expect(result).toEqual('no emojis in this prefix');
    });


    it("Emoji being parsed greater than emojiList", () => {
        fixSpacing();
        let result = parseEmojis(['{emoji-' + (emojiList.length + 1) + '}'], '{emoji-' + (emojiList.length + 1) + '}');
        expect(result).toEqual('{emoji-' + (emojiList.length + 1) + '}');
    });


    it("Convert variables and emojis to output", () => {
        // first change the default values
        document.getElementById('slackInput').value = '{emoji-' + (emojiList.length) + '} {name} {email} {channel} from Zulip |';
        document.getElementById('zulipInput').value = '{emoji-' + (emojiList.length) + '} {name} {email} {channel} from Slack |';

        // call display formatting on slack and zulip inputs
        displayFormatting('slackInput', 'slackOutput');
        displayFormatting('zulipInput', 'zulipOutput');

        // check input fields after
        expect(document.getElementById('slackInput').value).toEqual('{emoji-' + (emojiList.length) + '} {name} {email} {channel} from Zulip |');
        expect(document.getElementById('zulipInput').value).toEqual('{emoji-' + (emojiList.length) + '} {name} {email} {channel} from Slack |');

        // check output fields after
        expect(document.getElementById('slackOutput').innerHTML).toEqual(emojiList[emojiList.length - 1] + ' Fenton Reid fenton@reid.com meetings from Zulip |');
        expect(document.getElementById('zulipOutput').innerHTML).toEqual(emojiList[emojiList.length - 1] + ' Fenton Reid fenton@reid.com meetings from Slack |');
    });


    it("Valid emoji variables into emoji", () => {
        fixSpacing();
        for (let i = 0; i < emojiList.length; i++) {
            let result = parseEmojis(['{emoji-' + (i + 1) + '}'], '{emoji-' + (i + 1) + '}' + ' prefix');
            expect(result).toEqual(emojiList[i] + ' prefix');
        }
    });


    it("Checking resetToDefault button behaviour", () => {
        // first change the default values
        document.getElementById('slackInput').value = 'not default';
        document.getElementById('zulipInput').value = 'not default';

        expect(document.getElementById('slackInput').value).toEqual('not default');
        expect(document.getElementById('zulipInput').value).toEqual('not default');

        // invoke the resetToDefault button
        document.getElementById("resetToDefault").click();

        // check input fields
        expect(document.getElementById('slackInput').value).toEqual('{name} from Zulip |');
        expect(document.getElementById('slackOutput').innerHTML).toEqual('Fenton Reid from Zulip |');

        // check output fields
        expect(document.getElementById('zulipInput').value).toEqual('{name} from Slack |');
        expect(document.getElementById('zulipOutput').innerHTML).toEqual('Fenton Reid from Slack |');
    });


    it("Hidden fields set after submit", () => {
        // set input values
        document.getElementById('slackInput').value = '{emoji-' + (emojiList.length) + '} from Zulip |';
        document.getElementById('zulipInput').value = '{emoji-' + (emojiList.length) + '} from Slack |';

        // make call to submit field, it is disabled in this test from submitting
        $("#save").trigger("click");

        // check hidden fields and input fields
        expect(document.getElementById('slackInput').value).toEqual('{emoji-' + (emojiList.length) + '} from Zulip |');
        expect(document.getElementById('zulipInput').value).toEqual('{emoji-' + (emojiList.length) + '} from Slack |');

        expect(document.getElementById('slackHidden').value).toEqual(emojiList[emojiList.length - 1] + ' from Zulip |');
        expect(document.getElementById('zulipHidden').value).toEqual(emojiList[emojiList.length - 1] + ' from Slack |');
    });


    it("Check slack and zulip onInput behaviour", () => {
        // change slack and zulip inputs
        document.getElementById('slackInput').value = '{emoji-' + (emojiList.length) + '} {name} {email} {channel} from Zulip |';
        document.getElementById('zulipInput').value = '{emoji-' + (emojiList.length) + '} {name} {email} {channel} from Slack |';

        // trigger onInput event
        $("#slackInput").trigger("input");
        $("#zulipInput").trigger("input");

        // check output fields after
        expect(document.getElementById('slackOutput').innerHTML).toEqual(emojiList[emojiList.length - 1] + ' Fenton Reid fenton@reid.com meetings from Zulip |');
        expect(document.getElementById('zulipOutput').innerHTML).toEqual(emojiList[emojiList.length - 1] + ' Fenton Reid fenton@reid.com meetings from Slack |');
    });
});



/*  Rotate Arrow Tests*/
describe("Rotate Arrow Testing", () => {
    beforeAll(() => {
        let arrow = document.createElement('img');
        arrow.id = "arrow";
        arrow.setAttribute("onclick", "rotateArrow('arrow')");
        document.body.appendChild(arrow);
    });

    afterAll(() => {
        // remove Dom after all specs are complete
        document.getElementById('arrow').remove()
    });


    it("Default angle", () => {
        // transform should have no style
        expect(document.getElementById('arrow').style.transform).toEqual("");
    });


    it("Invoke transform", () => {
        // expect before
        expect(document.getElementById('arrow').style.transform).toEqual("");

        // trigger the rotation
        $("#arrow").trigger("click");

        // check the transform
        expect(document.getElementById('arrow').style.transform).toEqual("rotate(270deg)");
    });


    it("Invoke again", () => {
        // expect before
        expect(document.getElementById('arrow').style.transform).toEqual("rotate(270deg)");

        // trigger the rotation
        $("#arrow").trigger("click");

        // check the transform
        expect(document.getElementById('arrow').style.transform).toEqual("rotate(0deg)");
    });
});



/*  View Stored Information Tests*/
describe("View Stored Information Testing", () => {
    beforeEach(() => {
        let tokenInput = document.createElement('input');
        tokenInput.id = "tokenInput";
        tokenInput.placeholder = "*************";

        // adding onmouseover and onmouseleave events
        tokenInput.setAttribute("onmouseover", "onmouseOn('tokenInput', 'Hidden Text')")
        tokenInput.setAttribute("onmouseleave", "onmouseOff('tokenInput')")

        document.body.appendChild(tokenInput);
        document.getElementById("tokenInput").readOnly = true;
    });

    afterEach(() => {
        document.getElementById('tokenInput').remove();
    });

    it("Token input has default values when no action is performed", () => {
        expect(document.getElementById('tokenInput').placeholder).toEqual('*************');
        expect(document.getElementById('tokenInput').value).toEqual('');
    })

    it("Onmouseover shows hidden text", () => {
        $("#tokenInput").trigger("mouseover");
        expect(document.getElementById('tokenInput').value).toEqual('Hidden Text');
    });

    it("Onmouseleave shows default text", () => {
        $("#tokenInput").trigger("mouseleave");
        expect(document.getElementById('tokenInput').value).toEqual('*************');
    });
});



/* Run Tests*/
describe("Run Tests Testing", () => {
    beforeEach(() => {
        // create form
        let form = document.createElement('form');
        form.id = "form";
        form.method = "POST";
        form.setAttribute("onsubmit", "return showSpinner() & event.preventDefault();");

        /* create form children */

        // create check box
        let acceptBox = document.createElement('input');
        acceptBox.id = "acceptBox";
        acceptBox.type = "checkbox";
        acceptBox.setAttribute("onclick", "toggleButton()");

        // create button
        let runTestButton = document.createElement("button");
        runTestButton.id = "runTestButton";
        runTestButton.type = "submit";
        runTestButton.setAttribute("onclick", "document.getElementById('acceptBox').checked = false;");

        // create loadingSpinner
        let loadingSpinner = document.createElement('span');
        loadingSpinner.id = "loadingSpinner";

        /* add children to the form */
        form.appendChild(acceptBox);
        form.appendChild(runTestButton);

        // add items to the dom
        document.body.appendChild(form);
        document.body.appendChild(loadingSpinner);

        document.getElementById("loadingSpinner").style.display = "none";
        document.getElementById("runTestButton").disabled = true;
    });

    afterEach(() => {
        ['form', 'loadingSpinner'].forEach(e => document.getElementById(e).remove());
    });

    it("Token input has defaults", () => {
        expect(document.getElementById("loadingSpinner").style.display).toEqual("none");
        expect(document.getElementById("runTestButton").disabled).toBe(true);
    });

    it("Show spinner via function call", () => {
        showSpinner();
        // call the showSpinnerButton
        expect(document.getElementById("loadingSpinner").style.display).toEqual("inherit");
        expect(document.getElementById("runTestButton").disabled).toBe(true);
    });

    it("Form submission behaviour", () => {
        /* when the acceptBox is off */
        document.getElementById("acceptBox").checked = false;
        toggleButton();

        expect(document.getElementById("runTestButton").disabled).toBe(true);

        /* when the acceptBox is on */
        document.getElementById("acceptBox").checked = true;
        toggleButton();

        expect(document.getElementById("runTestButton").disabled).toBe(false);

    });

    it("Show spinner via form submit", () => {
        $('#form').trigger('submit');
        // call the showSpinnerButton
        expect(document.getElementById("loadingSpinner").style.display).toEqual("inherit");
        expect(document.getElementById("runTestButton").disabled).toBe(true);
    });
});


/* Integration Setup Tests*/
describe("Integration Setup Testing", () => {
    beforeEach(() => {
        let form = document.createElement("form");
        form.id = "form";
        form.method = "POST";
        form.action = "/integrationSetup/validate/slackAppToken";

        let tokenUpload = document.createElement("button");
        tokenUpload.id = "tokenUpload";

        let tokenSubmit = document.createElement("button");
        tokenSubmit.id = "tokenSubmit";

        // add button to form
        form.appendChild(tokenUpload);
        form.appendChild(tokenSubmit);
        // add items to dom
        document.body.appendChild(form);

        // giving initial values
        setUploadAttributes("tokenUpload", "NONE");
        setValidateAttributes("tokenSubmit", 'NONE', 'Not Uploaded');
        tokenSubmit.innerHTML = "Not Uploaded";
    });

    afterEach(() => {
        document.getElementById('form').remove();
    });

    it("Token input has defaults", () => {
        expect(document.getElementById('tokenUpload').className).toEqual("btn btn-info btn-sm");
        expect(document.getElementById('tokenUpload').innerHTML).toEqual("Setup");

        expect(document.getElementById('tokenSubmit').value).toEqual("Upload first");
        expect(document.getElementById('tokenSubmit').className).toEqual("btn btn-danger btn-sm");
        expect(document.getElementById('tokenSubmit').style.pointerEvents).toEqual("none");
    });

    it("None Token not given", () => {
        setUploadAttributes("tokenUpload", "non-default");
        setValidateAttributes("tokenSubmit", 'non-default', '');

        expect(document.getElementById('tokenUpload').className).toEqual("btn btn-success btn-sm");
        expect(document.getElementById('tokenUpload').innerHTML).toEqual("Done");

        expect(document.getElementById('tokenSubmit').value).toEqual("Upload first");
        expect(document.getElementById('tokenSubmit').style.pointerEvents).toEqual("none");
    });

    it("Validate attributes", () => {
        // not checked
        setValidateAttributes("tokenSubmit", 'non-default', 'Not Checked');
        expect(document.getElementById('tokenSubmit').className).toEqual("btn btn-warning btn-sm");

        // Invalid
        setValidateAttributes("tokenSubmit", 'non-default', 'Invalid');
        expect(document.getElementById('tokenSubmit').className).toEqual("btn btn-danger btn-sm");

        // Incomplete
        setValidateAttributes("tokenSubmit", 'non-default', 'Incomplete');
        expect(document.getElementById('tokenSubmit').className).toEqual("btn btn-secondary btn-sm");

        // Valid
        setValidateAttributes("tokenSubmit", 'non-default', 'Valid');
        expect(document.getElementById('tokenSubmit').className).toEqual("btn btn-success btn-sm");

        // Other
        setValidateAttributes("tokenSubmit", 'non-default', 'Other...');
        expect(document.getElementById('tokenSubmit').className).toEqual("btn btn-danger btn-sm");
    });
});




describe("registerZulipQueue", () => {
    beforeAll(() => {
        // create labels
        let zulipState = document.createElement('label');
        zulipState.id = "zulipState";

        let slackState = document.createElement('label');
        slackState.id = "slackState";

        // create labels
        let zulipStatus = document.createElement('img');
        zulipStatus.id = "zulipStatus";

        let slackStatus = document.createElement('img');
        slackStatus.id = "slackStatus";

        // create other
        let loadingSpinner = document.createElement('button');
        loadingSpinner.id = "loadingSpinner";

        let startButton = document.createElement('button');
        startButton.id = "startButton";

        let stopButton = document.createElement("button");
        stopButton.id = "stopButton";

        // add to dom
        document.body.appendChild(zulipState);
        document.body.appendChild(zulipStatus);

        document.body.appendChild(slackState);
        document.body.appendChild(slackStatus);

        document.body.appendChild(loadingSpinner);
        document.body.appendChild(startButton);
        document.body.appendChild(stopButton);
    });

    afterAll(() => ['slackState', 'slackStatus', 'zulipState', 'zulipStatus', 'loadingSpinner', 'startButton', 'stopButton'].forEach(e => document.getElementById(e).remove()));

    it("Integration defaults", () => {
        expect(socket).toBeDefined();
        expect(queue_id).toBeDefined();
        expect(lastEventID).toBe(-1);
        expect(controller).toBeInstanceOf(AbortController);
    });


    it("Fetch registerZulipQueue without queue_id", done => {
        let response = new Response(JSON.stringify({
            last_event_id: -1,
            msg: "",
            result: "success"
        }));

        // creating a fetch spy
        spyOn(window, 'fetch').and.returnValue(Promise.resolve(response));

        // make call to fetch
        registerZulipQueue()
            .then(zulipRegister => {
                expect(window.fetch).toHaveBeenCalledWith("\\api\\registerQueue", {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                })

                // as the queue_id is missing it is expected than an error was thrown
                expect(document.getElementById('zulipState').innerHTML).toEqual('<b>COULD NOT REGISTER QUEUE</b>');
                expect(document.getElementById('zulipStatus').src).toMatch('/static/images/redCircle.png');

                done();
            });
    });


    it("Fetch registerZulipQueue with queue_id", done => {
        let response = new Response(JSON.stringify({
            last_event_id: -1,
            msg: "",
            queue_id: '1517975029:0',
            result: "success"
        }));

        // creating a fetch spy
        spyOn(window, 'fetch').and.returnValue(Promise.resolve(response));

        // make call to fetch
        registerZulipQueue()
            .then(() => {
                expect(window.fetch).toHaveBeenCalledWith("\\api\\registerQueue", {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                })

                expect(queue_id).toEqual("1517975029:0");
                expect(document.getElementById('zulipState').innerHTML).toEqual("<b>RECEIVING</b>");
                expect(document.getElementById('zulipStatus').src).toMatch("/static/images/greenCircle.png");

                expect(window.fetch).toHaveBeenCalledWith("test/api/v1/events?queue_id=1517975029%3A0&last_event_id=-1", {
                    headers: {
                        'Authorization': 'Basic ' + btoa(zulipAuth.email + ':' + zulipAuth.key)
                    },
                    method: 'GET',
                    signal: controller.signal
                });
                done();
            });
    });
});


describe("registerSlackSocket without socketURL", () => {
    beforeAll(() => {
        // create labels
        let zulipState = document.createElement('label');
        zulipState.id = "zulipState";

        let slackState = document.createElement('label');
        slackState.id = "slackState";

        // create labels
        let zulipStatus = document.createElement('img');
        zulipStatus.id = "zulipStatus";

        let slackStatus = document.createElement('img');
        slackStatus.id = "slackStatus";

        // create other
        let loadingSpinner = document.createElement('button');
        loadingSpinner.id = "loadingSpinner";

        let startButton = document.createElement('button');
        startButton.id = "startButton";

        let stopButton = document.createElement("button");
        stopButton.id = "stopButton";

        // add to dom
        document.body.appendChild(zulipState);
        document.body.appendChild(zulipStatus);

        document.body.appendChild(slackState);
        document.body.appendChild(slackStatus);

        document.body.appendChild(loadingSpinner);
        document.body.appendChild(startButton);
        document.body.appendChild(stopButton);
    });

    afterAll(() => {
        ['slackState', 'slackStatus', 'zulipState', 'zulipStatus', 'loadingSpinner', 'startButton', 'stopButton'].forEach(e => document.getElementById(e).remove());
    });

    it("registerSlackSocket without socketURL", done => {
        //mock the next fetch call
        spyOn(window, 'fetch').and.returnValue(Promise.resolve(new Response()));

        // make call to fetch
        registerSlackSocket()
            .then(slackSocket => {
                // check the fetch arguments
                expect(window.fetch).toHaveBeenCalledWith("\\api\\registerSocket", {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                })

                // as socketURL is missing expect that the catch has been called
                expect(document.getElementById('slackState').innerHTML).toEqual("<b>COULD NOT REGISTER SOCKET</b>");
                expect(document.getElementById('slackStatus').src).toMatch('/static/images/redCircle.png');

                done();
            });
    });


    it("Fetch registerSlackSocket with socketURL", done => {
        // create expected response
        let response = new Response(JSON.stringify({
            socketURL: "wss://wss-something.slack.com/"
        }));

        // mock registerSlackSocket fetch
        spyOn(window, 'fetch').and.returnValue(Promise.resolve(response));

        // mock WebSocket as it is expected that the response is correct
        spyOn(window, 'WebSocket').and.returnValue(new WebSocket);

        // make call to fetch
        registerSlackSocket()
            .then(slackSocket => {
                // check the fetch arguments
                expect(window.fetch).toHaveBeenCalledWith("\\api\\registerSocket", {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                })

                // create a test event
                var event = {
                    data: {
                        envelope_id: '___',
                        payload: {
                            event: "xxx"
                        },
                        retry_attempt: 0
                    },
                };
                done();
            });
    });


    it("socket open", () => {
        // call the mock socket and observe behaviour
        socket.onopen();

        expect(document.getElementById('slackState').innerHTML).toEqual("<b>RECEIVING</b>");
        expect(document.getElementById('slackStatus').src).toMatch('/static/images/greenCircle.png');
    });


    it("socket onmessage without envelope_id", () => {
        var event = JSON.stringify({
            payload: {
                event: "rename_channel",
            },
            retry_attempt: 0,
        });

        expect(socket.onmessage({
            data: event
        })).toEqual("missing envelope_id");
    });


    it("socket onmessage invoke catch to innerFetch", () => {
        var event = JSON.stringify({
            envelope_id: 'xxx:xxx',
            payload: {
                event: "rename_channel",
            },
            retry_attempt: 0,

        });

        // mock socket.send with null value
        socket.send = () => null;

        // create a onmessage spy
        let onmessageSpy = spyOn(socket, 'onmessage').and.callThrough();

        // create a promise that will automatically catch
        let failedPromise = new Promise(() => {
            reject
        });

        // create a spy for the inner \slackEvents fetch
        let innerFetchSpy = spyOn(window, 'fetch').and.returnValue(failedPromise);

        // send message
        socket.onmessage({
            data: event
        });
        expect(onmessageSpy).toHaveBeenCalledWith({
            data: event
        });

        // check the inner fetch arguments
        expect(innerFetchSpy).toHaveBeenCalledWith("\\api\\slackEvents", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                event: "rename_channel",
            })
        });

        // invoke .catch on the promise
        failedPromise.catch(() => expect(document.getElementById('slackState').innerHTML).toEqual('<b>CLOSED BY EXCEPTION</b>'));
    });


    it("socket onmessage invoke resolve ", () => {
        var event = JSON.stringify({
            envelope_id: 'xxx:xxx',
            payload: {
                event: "rename_channel",
            },
            retry_attempt: 0,

        });

        // mock socket.send with null value
        socket.send = () => null;

        // create a onmessage spy
        let onmessageSpy = spyOn(socket, 'onmessage').and.callThrough();

        // create a promise that will resolve correctly (not invoke catch)
        let resolvedPromise = new Promise(() => {
            resolve
        });

        // create a spy for the inner \slackEvents fetch
        let innerFetchSpy = spyOn(window, 'fetch').and.returnValue(resolvedPromise);

        // send message
        let socketMessage = socket.onmessage({
            data: event
        });
        expect(onmessageSpy).toHaveBeenCalledWith({
            data: event
        });

        // check the inner fetch arguments
        expect(innerFetchSpy).toHaveBeenCalledWith("\\api\\slackEvents", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                event: "rename_channel",
            })
        });
        expect(socketMessage.PromiseResult).not.toBeDefined();
    });

    
    it("socket close behaviour", () => {
        // call the mock socket and observe behaviour
        socket.onclose();
        expect(document.getElementById('slackState').innerHTML).toEqual("<b>CLOSED</b>");
        expect(document.getElementById('slackStatus').src).toMatch('/static/images/redCircle.png');
    });
});

/* Emoji Additions Testing*/
describe("Emoji Additions Testing", () => {
    beforeAll(() => {
        // create inputs
        let addSlack = document.createElement("input");
        addSlack.id = "addSlack";

        let addZulip = document.createElement("input");
        addZulip.id = "addZulip";

        // add to DOM
        document.body.appendChild(addSlack);
        document.body.appendChild(addZulip);
    });

    afterAll(() => ['addSlack', 'addZulip'].forEach(e => document.getElementById(e).remove()));

    it("Default values", () => {
        document.getElementById("addSlack").value = ":heart:";
        document.getElementById("addZulip").value = ":heart:";

        addMapping();

        expect( document.getElementById("addSlack").style)

    });

    it("Invalid emoji values", () => {
        document.getElementById("addSlack").value = "not valid";
        document.getElementById("addZulip").value = ":O";
        addMapping();

        expect(document.getElementById("addSlack").style.backgroundColor).toMatch("red");
        expect(document.getElementById("addZulip").style.backgroundColor).toMatch("red");
        expect(addMapping()).toEqual(false);


        document.getElementById("addSlack").value = ":invalid0:";
        document.getElementById("addZulip").value = ":invalid:";
        addMapping();

        expect(document.getElementById("addSlack").style.backgroundColor).toMatch("red");
        expect(document.getElementById("addZulip").style.backgroundColor).toMatch("red");
        expect(addMapping()).toEqual(false);
    });

    it("Valid emoji values", () => {
        document.getElementById("addSlack").value = ":heart:";
        document.getElementById("addZulip").value = ":heart:";
        addMapping();

        expect(document.getElementById("addSlack").style.backgroundColor).toMatch("white");
        expect(document.getElementById("addZulip").style.backgroundColor).toMatch("white");
        expect(addMapping()).toEqual(true);
    });
});