// private_socketio.js

$(document).ready(function () {
    let chat_socket = io.connect("/chat_now");
    let $messageArea = $("#chat-messages");

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

    chat_socket.on('chat_message', function (data) {
        addMessage(data, data.friendname === username);
    });

    chat_socket.on("message", (data) => {
        let contentP = `
            <div class="text">
                <span style="text-align:center; display:flex;justify-content:center; color:#e88d67">
                  <strong>${data.name}</strong>  ${data.msg}
                </span>
            </div>`;
        messages.append(contentP);
    });

    $("#chat-message-form").submit(function (e) {
        e.preventDefault();
        let msg = $("#message-input").val();
        if (msg == "") return;
        chat_socket.emit("sent_message", { "msg": msg, "friendname": username, 'code': chat_code });
        msg.val("");
    });
});
