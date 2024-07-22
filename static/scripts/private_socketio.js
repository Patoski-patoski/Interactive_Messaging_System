// private_socketio.js
$(document).ready(function () {
    let chat_socket = io.connect("/chat_now");
    let $messageArea = $('#chat-messages');

    $("#chat-message-form").submit(function (e) {
        e.preventDefault();
        let msg = $("#message-input").val();
        if (msg.trim() !== '') {
            chat_socket.emit("sent_message", { "msg": msg, "username": username, 'code': code });
            $('#message-input').val('');
        }
    });

    function insertMessage(data, own = false) {
        let msgDiv = $('<div>').addClass('message');
        if (own) msgDiv.addClass('own');
        let usernameSpan = $('<span>').addClass('username').text(data.username);
        let timeSpan = $('<span>').addClass('time').text(data.created_at);
        let contentP = $('<p>').addClass('content').text(data.msg);
        msgDiv.append(usernameSpan, timeSpan, contentP);


        $messageArea.append(msgDiv);
        $messageArea.scrollTop(($messageArea)[0].scrollHeight);
    }

    chat_socket.on('message', function (data) {
        insertMessage(data, data.username === username);
    });

    chat_socket.on("on_join", (data) => {
        let contentP = `
            <div class="text">
                <span style="text-align:center; display:flex;justify-content:center; color:#e88d67">
                  <strong>${data.name}</strong>  ${ data.msg}
                </span>
            </div>`;
        $messageArea.append(contentP);
    });
});