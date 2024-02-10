var $textarea = $(".content");
var content = $textarea.val();
$(".print").text(content);
const page = decodeURIComponent(window.location.pathname.substring(1));

var socket;
$(document).ready(function(){
    socket = io.connect('/note-ws');

    socket.on('connect', () => {
        socket.emit('join',{'page': page});
    })

    socket.on('text_broadcast', (data) => {
        $textarea.val(data.text);
    });

    area = document.querySelector('textarea');
    area.addEventListener('input', () => {
        socket.emit('text_post', {'page':page, 'text':$textarea.val()});
        $(".print").text(content);
    }, false);

});