let tasks = []
let deltas=[]

function move_room(new_room_id, new_room_name) {
    window.history.pushState({}, "Title", "/room/" + new_room_id);
    document.getElementById("room_name").innerHTML = new_room_name;
    document.getElementById("messages").innerHTML="Loading..."
    room_id = new_room_id;
    
    index = tasks.indexOf("get_messages")
    if (index != -1) {
        tasks.splice(index, 1);
    }
    
    new_task("recolor", room_id)
    ping_very_important()
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function check_disconnected() {
    if (socket.connected) {
        if (!document.getElementById("disconnected").classList.contains("hidden")) {
            toggleOption("disconnected");
            return false;
        }
        return true;
    }
    else {
        // check if #disconnected has hidden class
        if (document.getElementById("disconnected").classList.contains("hidden")) {
            toggleOption("disconnected");
            return false;
        }
    }
}

function autoscroll() {
    var element = document.getElementById("messages");
    element.scrollTop = element.scrollHeight;
}

function new_task(emit, params) {
    if (!tasks.includes(emit)) {
        tasks.push(emit)
        socket.emit(emit, {"params": params, "pong": emit})
    }
}

function ping() {
    new_task("connected", room_id)
}

function ping_important() {
    new_task("get_online")
    new_task("get_rooms")
}

function ping_very_important() {
    new_task("get_messages", room_id)
}

function status() {
    socket.emit("connected")
}

socket.onAny((event, args) => {
    if (tasks.includes(event)) {
        var index=tasks.indexOf(event)
        tasks.splice(index, 1)
    }
})

socket.on("recieve_rooms", function (data) {
    document.getElementById("chatrooms").innerHTML=data["rooms"];
})

socket.on("recieve_online", function (data) {
    document.getElementById("current-online").innerHTML = data["online"];
})

socket.on("recieve_messages", function (data) {
    if (data["room_id"] == room_id) {
        document.getElementById("messages").innerHTML = data["messages"];;
        autoscroll()
    }
})

socket.on("recieve_local_message", function (data) {
    var e = document.createElement("local");
    e.innerHTML = data["message"]
    document.getElementById("messages").appendChild(e)
})

socket.on("redirect", function (data) {
    window.location="/";
})

socket.on("maintenance", function (data) {
    window.location = "/maintenance"
    document.getElementById("loading-screen").innerHTML = "Currently in maintenance mode, redirecting you...";
    document.getElementById("loading-screen").className = "unload";
})

socket.on("new_messages", function (data) {
    if (data["room_id"] == room_id) {
        autoscroll();
    }
})

socket.on("clear tasks", function (data) {
    console.log("Cleared Tasks")
    tasks.length = 0;
})

// Forcefully sends a socketio emit to server itself due to limitations.
socket.on("force", function (data) {
    socket.emit(data["name"], data["params"])
})

socket.on("force disconnect", function (data) {
    console.log("SERVER INITIATED FORCE DISCONNECT.")
    socket.disconnect()
    window.location="/";
})

setInterval(check_disconnected, 5000)
setInterval(ping, 1000)
setInterval(ping_important, 5000)