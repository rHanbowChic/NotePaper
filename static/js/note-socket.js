// 需要 jQuery 2.2.4 与 SocketIO 4.7.4。在模板'note.html'中，这两个依赖被script标签引用。

var $textarea = $(".content");
$(".print").text($textarea.val());
// page为页面名。例如http://hostname/odyu为'odyu'。
const page = decodeURIComponent(window.location.pathname.substring(1));

var socket;
$(document).ready(function(){
    socket = io.connect('/note-ws');
    // 加入到room
    socket.on('connect', () => {
        socket.emit('join',{'page': page});
    })
    // 接收到服务器的广播后，更新页面内容
    socket.on('text_broadcast', (data) => {
        $textarea.val(data.text);
    });
    // 用户修改页面内容后，发送内容到服务器
    area = document.querySelector('textarea');
    area.addEventListener('input', () => {
        socket.emit('text_post', {'page':page, 'text':$textarea.val()});
        $(".print").text($textarea.val());
    }, false);

});