// socketio.js
let room = "Coding";

$(document).ready(function () {
    let socket = io();

    // Join default room on load
    joinRoom(room);

    socket.on('message', data => {
        let p = $('<p>');
        let span_username = $('<span>').text(data.username);
        let span_time = $('<span>').text(data.created_at);
        p.html(span_username.html() + '<br>' + data.msg + '<br>' + span_time.html());
        $("#display-msg").append(p);

    });

    // Handle chat history
    socket.on('chat_history', function (messages) {
        $("#display-msg").html(""); // Clear the chat window
        for (let message of messages) {
            let p = $('<p>');
            let span_username = $('<span>').text(message.username);
            let span_time = $('<span>').text(message.created_at);
            p.html(span_username.html() + '<br>' + message.msg + '<br>' + span_time.html());
            $("#display-msg").append(p);
        }
    });

    $("#send").click(function () {
        let msg = $('#user-msg').val();
        socket.send(({ 'msg': msg, 'username': username, 'created_at': created_at, 'room': room }));
        $('#user-msg').val("");
    });

    // Change rooms
    $(".select-room").each(function () {
        $(this).click(function () {
            let newRoom = $(this).text();
            if (newRoom === room) {
                msg = `You are in the (${room}) room already!`;
                printSysMsg(msg);

            } else {
                leaveRoom(room);
                joinRoom(newRoom);
                room = newRoom;
            }
        });
    });

    function leaveRoom(room) {
        socket.emit('leave', { 'username': username, 'room': room });
    }

    function joinRoom(room) {
        socket.emit('join', { 'username': username, 'room': room });
        $("#display-msg").html("");
    }

    function printSysMsg(msg) {
        let p = $('<p class="system-msg">').text(msg);
        $("#display-msg").append(p);
    }
});