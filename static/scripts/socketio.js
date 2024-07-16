
//socketio.js
$(document).ready(function () {
    let socket = io.connect('/room_chat');
    let private_socket = io.connect('/add_friend');

    let $messageArea = $('#message-area');
    let room_list_def = ["General", "Technology", "Philosphy"]


    /////////
    //////// Room Chat /////////
    /////////


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

    $('#message-form').submit(function (e) {
        e.preventDefault();
        let msg = $('#user-msg').val();
        if (msg.trim() !== '') {
            socket.emit('message', { 'msg': msg, 'username': username, 'room': currentRoom });
            $('#user-msg').val('');
        }
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



    //////// Private Chat /////////


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

    private_socket.on('message', function (data) {
        addMessage(data, data.username === username)
    });

    private_socket.on('chat_history', function (messages) {
        $('#message-area').empty();
        messages.forEach(function (message) {
            addMessage(message, message.username === username);
        });
    });

    function joinFriend(friend) {
        private_socket.emit('join', { 'username': username, 'friend': friend });
        $('#current-friend').text(friend);
        currentRoom = friend;
    }

    $('#message-form').submit(function (e) {
        e.preventDefault();
        let msg = $('#user-msg').val();
        if (msg.trim() !== '') {
            private_socket.emit('message', { 'msg': msg, 'username': username, 'friend': currentRoom });
            $('#user-msg').val('');
        }
    });

    private_socket.on("loaded", (friend_list) => {
        for (let index = 0; index < friend_list_def.length; index++) {
            friend_list.push(friend_list_def[index])
        }
        friend_list.forEach(function (friend) {
            let friendItem = $('<li>').addClass('list-group-item').text(friend);
            friendItem.click(function () {
                $('#friend-list').empty();
                joinFriend(friend);
            });
            $('#friend-list').append(friendItem);
        });
    });


    
});