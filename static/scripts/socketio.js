
//socketio.js
$(document).ready(function () {
    let socket = io.connect('/room_chat');

    let $messageArea = $('#message-area');
    let room_list_def = ["General", "Technology", "Philosphy"]

    $('#message-form').submit(function (e) {
        e.preventDefault();
        let msg = $('#user-msg').val();
        if (msg.trim() !== '') {
            socket.emit('message', { 'msg': msg, 'username': username, 'room': currentRoom });
            $('#user-msg').val('');
        }
    });

    function addMessage(data, own = false) {
        let messageDiv = $('<div>').addClass('message');
        if (own) messageDiv.addClass('own');
        let usernameSpan = $('<span>').addClass('username').text(data.username);
        let timeSpan = $('<span>').addClass('time').text(data.created_at);
        let contentP = $('<p>').addClass('content').text(data.msg);
        messageDiv.append(usernameSpan, timeSpan, contentP);

        $($messageArea).append(messageDiv);
        $($messageArea).scrollTop(($messageArea)[0].scrollHeight);
    }

    socket.on('message', function (data) {
        addMessage(data, data.username === username);
    });

    function joinRoom(room) {
        socket.emit('join', { 'username': username, 'room': room });
        $('#current-room').text(room);
        currentRoom = room;
    }

    socket.on('chat_history', function (messages) {
        $('#message-area').empty();
        messages.forEach(function (message) {
            addMessage(message, message.username === username);
        });
    });
    
    socket.on("loaded", (room_list) => {
        for (let index = 0; index < room_list_def.length; index++) {
            room_list.push(room_list_def[index])
        }
        room_list.forEach(function (room) {
            let roomItem = $('<li>').addClass('list-group-item').text(room);
            roomItem.click(function () {
                $('#room-list').empty();
                joinRoom(room);
            });
            $('#room-list').append(roomItem);
        });
    });

    // Join default room
    joinRoom('General');
});