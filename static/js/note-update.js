var $ = document.querySelector.bind(document);  // RIP jQuery, NotePaper would never be possible without you
var url_params = new URLSearchParams(window.location.search);

var $textarea = $("textarea.content");
$textarea.focus();
$(".print").innerText = $textarea.value;
// page为页面名。例如http://hostname/odyu为'odyu'。
let page1 = "";  // conflicted with the "page" in md_client.js. an ugly workaround but I have no time to refactor it
if (window.location.pathname.startsWith("/v/")) {
    page1 = decodeURIComponent(window.location.pathname.substring(3)); // "/v/"
}
else {
    page1 = decodeURIComponent(window.location.pathname.substring(1)); // "/"
}

const pass = url_params.get("pass");

// 这是此 JS 由 live viewer 引用的情况。
if (window.location.pathname.startsWith("/v/"))
    (async () => {
        $("textarea.content").value =
            (await (await fetch("/papyrus/file/" + page1, {method: "GET",})).json()).text;
    })();

var socket;
document.addEventListener('DOMContentLoaded', function() {
    socket = io.connect('/note-ws');
    // 加入到room
    socket.on('connect', () => {
        socket.emit('join',{'page': page1});
    })
    // 接收到服务器的广播后，更新页面内容
    socket.on('text_broadcast', (data) => {
        // 更新后保留原先光标位置
        let pos = get_pos(".content");
        $textarea.value = data.text;
        set_pos(".content", pos);
        if (!window.location.pathname.startsWith("/v/"))
            $(".print").innerText = $textarea.value;
    });
    // 用户修改页面内容后，发送内容到服务器
    area = document.querySelector('textarea');
    area.addEventListener('input', () => {
        if (!window.location.pathname.startsWith("/v/"))
            $(".print").innerText = $textarea.value;
        if (pass) {
            socket.emit('text_post', {'page':page1, 'text':$textarea.value, 'pass':pass});
        }
        else {
            socket.emit('text_post', {'page':page1, 'text':$textarea.value});
        }
    }, false);
});

function get_pos(selector) {
    // 返回光标所在的行数与列数
    let lines_before_cursor = $(selector).value.substring(0, $(selector).selectionStart).split('\n');
    return [lines_before_cursor.length, lines_before_cursor[lines_before_cursor.length-1].length];
}

function set_pos(selector, pos) {
    // 设置光标到指定坐标
    let l = pos[0];
    let c = pos[1];
    let passage = $(selector).value;
    let lines = passage.split('\n');
    if (lines.length < l) {
        set_index(selector, passage.length);
        return;
    }
    let char_idx = Math.min(lines[l-1].length, c);
    let idx = 0;
    for (let i=0;i<l-1;i++) {
        idx += (lines[i].length + 1);  // '\n'
    }
    idx += char_idx;
    set_index(selector, idx);
}

function set_index(selector, index) {
    // 设置光标到指定index
    if ($(selector).selectionStart < index) {
        $(selector).selectionStart = index;
    }
    else {
        $(selector).selectionEnd = index;
    }
}
