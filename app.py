from flask import Flask
from flask import render_template
from flask import g
from flask import request
from flask import redirect
from flask import Response
from flaskext.markdown import Markdown
from flask_socketio import SocketIO, join_room, emit, leave_room
from bs4 import BeautifulSoup
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
    soup = BeautifulSoup(text, "html.parser")
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


@app.route("/<page>", methods=['GET'])
def page_get(page):
    cur = get_db().cursor()
    if page.endswith(".md"):  # /example1.md
        page = page[0:-3]  # example1
        text = cur.execute("select text from pages where id = ?", (page,)).fetchall()
        if len(text) == 0:  # 如果数据库没有记录
            text = ""
        else:
            text = text[0][0]
        # 过滤可能的XSS
        text = sanitize_html(text)

        if (request.headers.get("User-Agent") is not None and (
            "curl/" in request.headers.get("User-Agent")
            or "Wget/" in request.headers.get("User-Agent")
        )):  # 给curl与wget直接显示内容
            return Response(text, mimetype='text/plain')
        else:
            return render_template('note_md.html', page=page, text=text)
    else:
        text = cur.execute("select text from pages where id = ?", (page,)).fetchall()
        if len(text) == 0:
            text = ""
        else:
            text = text[0][0]

        is_text_request = request.args.get('text') is not None
        if (request.headers.get("User-Agent") is not None and (
            "curl/" in request.headers.get("User-Agent")
            or "Wget/" in request.headers.get("User-Agent")
            or is_text_request
        )):  # 给带有text参数的请求始终直接显示内容
            return Response(text, mimetype='text/plain')
        else:
            return render_template('note.html', page=page, text=text)


@app.route("/<page>", methods=['POST'])  # 兼容目的
def note_post(page):
    cur = get_db().cursor()
    # 正常情况下，浏览器永远不会对以.md结尾的页面发送POST请求。但不排除使用其他程序的情况。
    if not page.endswith(".md"):
        t = request.form.get("t")
        if t is not None:
            cur.execute("insert or replace into pages values(?, ?);", (page, t))
            get_db().commit()
    return ""


@app.route("/", methods=['GET'])
def root_redirect():
    randword = ""
    for i in range(4):
        randword += random.choice(string.ascii_lowercase)
    return redirect(f"./{randword}", code=302)


@socketio.on("join", namespace="/note-ws")
def join(message): join_room(message['page'])


@socketio.on("left", namespace="/note-ws")
def left(message): leave_room(message['page'])


@socketio.on("text_post", namespace="/note-ws")
def text_post(message):
    room = message['page']
    cur = get_db().cursor()
    cur.execute("insert or replace into pages values(?, ?);", (message['page'], message['text']))
    get_db().commit()  # 这个阻塞吗？
    emit("text_broadcast", {"text": message['text']}, to=room, broadcast=True, include_self=False)


if __name__ == "__main__":
    socketio.run(app)
