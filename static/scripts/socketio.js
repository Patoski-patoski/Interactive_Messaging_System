$(document).ready(function () {
    let socket = io();
    let room_list_def = ["General", "Technology", "Philosphy"]
    

    function addMessage(data, own = false) {
        let messageDiv = $('<div>').addClass('message');
        if (own) messageDiv.addClass('own');
        let usernameSpan = $('<span>').addClass('username').text(data.username);
        let timeSpan = $('<span>').addClass('time').text(data.created_at);
        let contentP = $('<p>').addClass('content').text(data.msg);
        messageDiv.append(usernameSpan, timeSpan, contentP)

        $('#message-area').append(messageDiv);
        $('#message-area').scrollTop($('#message-area')[0].scrollHeight);
    }

    socket.on('message', function (data) {
        addMessage(data, data.username === username);
    });

    socket.on('chat_history', function (messages) {
        $('#message-area').empty();
        messages.forEach(function (message) {
            addMessage(message, message.username === username);
        });
    });

    function joinRoom(room) {
        socket.emit('join', { 'username': username, 'room': room });
        $('#current-room').text(room);
        currentRoom = room;
    }

    socket.on("loaded", (room_list) => {
        for (let index = 0; index < room_list_def.length; index++) {
            room_list.push(room_list_def[index])
        }
        room_list.forEach(function (room) {
            let roomItem = $('<li>').addClass('list-group-item').text(room);
            roomItem.click(function () {
                $('#room-list').empty();
                joinRoom(room);
                // room_list_def = []
            });
            $('#room-list').append(roomItem);
        });
    });

    // Join default room
    joinRoom('General');

});