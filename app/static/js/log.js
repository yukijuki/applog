function posts_post_api(entry) {
    fetch(`${window.href}`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(entry),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    }) 
    .then(function (response) {

        if (response.status != 200) {
            console.log(`response status was not 200: ${response.status}`);
            return ;
        }

        response.json().then(function (data) {
            location.reload();
            console.log("fetched data", data)
        })
    })
}

async function log_post(id) {

    var screen_id = id;
    const event_category = document.getElementById("event_category").value;
    const event_action = document.getElementById("event_action").value;
    const firebase_screen = document.getElementById("firebase_screen").value;
    const event_label = document.getElementById("event_label").value;
    const event_label2 = document.getElementById("event_label2").value;
    var custom_event = document.getElementById("custom_event").checked;
    var screen_view = document.getElementById("screen_view").checked;

    var event_name;

    if (custom_event == true) {
        event_name = "custom_event"
    } else if(screen_view == true) {
        event_name = "screen_view"
    } else {
        event_name = "Unknown"
    }

    var entry = 
        {
            screen_id: screen_id,
            event_name: event_name,
            event_category: event_category,
            event_action: event_action,
            firebase_screen: firebase_screen,
            event_label: event_label,
            event_label2: event_label2

        }

    let response = await posts_post_api(entry)
    console.log("Posted Succesfully");

}

function delete_log(log_id, screen_id) {

    var entry = 
        {
            log_id: log_id,
            screen_id: screen_id
        }
    console.log(log_id)

    fetch(`${window.origin}/delete_log`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(entry),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    }) 
    .then(function (response) {

        if (response.status != 200) {
            console.log(`response status was not 200: ${response.status}`);
            return ;
        }

        response.json().then(function (data) {
            location.reload();
            console.log("fetched data", data)
        })
    })
}

function delete_screen(screen_id) {

    var entry = 
        {
            screen_id: screen_id
        }
    console.log(screen_id)

    fetch(`${window.origin}/delete_screen`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(entry),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    }) 
    .then(function (response) {

        if (response.status != 200) {
            console.log(`response status was not 200: ${response.status}`);
            return ;
        }

        response.json().then(function (data) {
            window.location.assign(`${window.origin}/screen`);
            console.log("fetched data", data)
        })
    })
}