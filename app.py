
from flask import Flask
from flask import render_template
from flask import g
from flask import request
from flask import redirect
from flask import Response
from flaskext.markdown import Markdown
from flask_socketio import SocketIO, join_room, emit, leave_room
from bs4 import BeautifulSoup
import utils.tex
import sqlite3
import random  # 最好的模块
import string

app = Flask(__name__)
Markdown(app)
socketio = SocketIO(app)


DATABASE = 'data/note_paper.sqlite'


VALID_TAGS = ['strong', 'em', 'p', 'ul', 'ol', 'li', 'b', 'i',
              'br', 'sub', 'sup', 'ruby', 'rt', 'rp', 'details', 'summary']


# 通过去除除VALID_TAGS外所有的标签与VALID_TAGS标签的所有属性来避免XSS攻击。
def sanitize_html(text):
    # 这是BeautifulSoup。
    soup = BeautifulSoup(text, "html.parser")
    # 遍历所有HTML标签，如果在VALID_TAGS中，则保留标签但删除所有属性（防止诸如onclick等属性的脚本执行）
    # 如果不在，则删除标签（在hidden设置为True时输出文本）
    for tag in soup.findAll(True):
        if tag.name in VALID_TAGS:
            lst = []
            for attr in tag.attrs:
                lst.append(attr)
            for attr in lst:
                del tag[attr]
        else:
            tag.hidden = True

    return soup.renderContents().decode('utf-8')


# 连接到SQLite数据库
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


# 关闭上下文时关闭SQLite连接
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# 笔记页面的GET方法。使用浏览器访问笔记页面（如http://hostname/a）时触发。
@app.route("/<page>", methods=['GET'])
def page_get(page):
    # 获得一个执行SQL语句的SQlite cursor。get_db是在前文声明的。
    cur = get_db().cursor()
    # 如果以.md结尾，则渲染markdown并输出HTML作为模板的一部分。（templates/note_md.html）
    if page.endswith(".md"):  # /example1.md
        page = page[0:-3]  # example1
        text = cur.execute("select text from pages where id = ?", (page,)).fetchall()
        if len(text) == 0:  # 如果数据库没有记录
            text = ""
        else:
            text = text[0][0]
        # 将TeX公式转换为Markdown图片
        text = utils.tex.tex_to_markdown(text)
        # 过滤可能的XSS
        text = sanitize_html(text)

        if (request.headers.get("User-Agent") is not None and (
            "curl/" in request.headers.get("User-Agent")
            or "Wget/" in request.headers.get("User-Agent")
        )):  # 给curl与wget直接显示内容
            return Response(text, mimetype='text/plain')
        else:
            return render_template('note_md.html', page=page, text=text)
    else:  # 如果不以.md结尾，则返回笔记页面。（templates/note.html）
        text = cur.execute("select text from pages where id = ?", (page,)).fetchall()
        if len(text) == 0:
            text = ""
        else:
            text = text[0][0]

        is_text_request = request.args.get('text') is not None
        is_mono_request = request.args.get('m') is not None or request.args.get('mono') is not None
        if (request.headers.get("User-Agent") is not None and (
                "curl" in request.headers.get("User-Agent")
                or "Wget" in request.headers.get("User-Agent")
                or is_text_request
        )):  # 给带有text参数的请求始终直接显示内容
            return Response(text, mimetype='text/plain')
        elif is_mono_request:
            return render_template('note_mono.html', page=page, text=text)
        else:
            return render_template('note.html', page=page, text=text)


# 笔记页面的POST方法。在原版Notems中，这是更新笔记的唯一方法。NotePaper使用Socket.IO更新笔记内容，但此方法因兼容目的被保留。
# 如果你不想要POST更新，可以安全删除@app.route和以下的整个note_post()函数。
@app.route("/<page>", methods=['POST'])
def note_post(page):
    cur = get_db().cursor()
    # 正常情况下，浏览器永远不会对以.md结尾的页面发送POST请求。但不排除使用其他程序的情况。
    if not page.endswith(".md"):
        t = request.form.get("t")
        if t is not None:
            cur.execute("insert or replace into pages values(?, ?);", (page, t))
            get_db().commit()
    return ""


# 访问根目录时触发。302跳转到一个随机的4位小写字母页面。
@app.route("/", methods=['GET'])
def root_redirect():
    randword = ""
    for i in range(4):
        randword += random.choice(string.ascii_lowercase)
    return redirect(f"./{randword}", code=302)


# Socket.IO 加入房间。浏览器端的JS在页面完成加载时传递信息，‘page’为所在的页面。例如http://hostname/odyu为‘odyu’。
# 服务器接收到消息后会加入room。此后服务器可向此页面的room发送消息。
@socketio.on("join", namespace="/note-ws")
def join(message): join_room(message['page'])


# Socket.IO离开房间。目前此方法永远不会被调用！因为用户关闭窗口时无法执行特定的JS。
# 但Socket.IO会在浏览器端一段时间无响应后自动离开房间。
@socketio.on("left", namespace="/note-ws")
def left(message): leave_room(message['page'])


# 浏览器端检测到页面变更时发送的消息，包含页面名与更新的笔记内容。
# 服务器会将已更新的笔记发送到页面对应room中所有的浏览器端。
@socketio.on("text_post", namespace="/note-ws")
def text_post(message):
    room = message['page']
    cur = get_db().cursor()
    cur.execute("insert or replace into pages values(?, ?);", (message['page'], message['text']))
    get_db().commit()  # 这个阻塞吗？
    emit("text_broadcast", {"text": message['text']}, to=room, broadcast=True, include_self=False)


if __name__ == "__main__":
    socketio.run(app)
