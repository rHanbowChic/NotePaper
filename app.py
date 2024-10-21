from flask import Flask
from flask import render_template
from flask import g
from flask import request
from flask import redirect
from flask import Response
from flask_socketio import SocketIO, join_room, emit, leave_room
import utils
import sqlite3

from blueprints.share import share
from config import *

app = Flask(SITE_NAME)
socketio = SocketIO(app)
if USE_SHARE:
    app.register_blueprint(share, url_prefix="/s/")


DATABASE = 'data/note_paper.sqlite'


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
    # 如果以.md结尾，渲染Markdown。
    if page.endswith(".md"):  # /example1.md
        # 返回一个静态客户端，从md_api获取文本并进行前端渲染。（templates/md_client.j2）
        return render_template("paper.html", body="md_client", site_name=SITE_NAME)
    else:  # 如果不以.md结尾，则返回笔记页面。（templates/note.j2）
        text = cur.execute("select text from pages where id = ?", (page,)).fetchall()
        if len(text) == 0:
            text = ""
        else:
            text = text[0][0]
        return utils.text2resp(app, page, text, SITE_NAME, 'note')


# 笔记页面的POST方法。在原版Notems中，这是更新笔记的唯一方法。NotePaper使用Socket.IO更新笔记内容，但此方法因兼容目的被保留。
# 如果你不想要POST更新，可以安全删除@app.route和以下的整个note_post()函数。
@app.route("/<page>", methods=['POST'])
def note_post(page):
    cur = get_db().cursor()
    # 正常情况下，浏览器永远不会对以.md结尾的页面发送POST请求。但不排除使用其他程序的情况。
    if not (page.endswith(".md") or page in PROTECTED_PAGES):
        t = request.form.get("t")
        if t is not None and len(t) < PAGE_MAX_LENGTH:
            cur.execute("insert or replace into pages values(?, ?);", (page, t))
            get_db().commit()
    return ""


# 访问根目录时触发。302跳转到一个随机的4位小写字母页面或2个单词组成的页面。
@app.route("/", methods=['GET'])
def root_redirect():
    if SHOW_WELCOME:
        if not request.cookies.get("have_visited"):
            response = redirect(f"./{WELCOME_PAGE}", code=302)
            response.set_cookie("have_visited", value="1")
            return response
    if request.args.get('w') is not None or request.args.get('words') is not None:
        response = redirect(f"./{utils.genname_words()}", code=302)
        response.set_cookie("prefer_words_redirect", value="1")
        return response
    if request.args.get('l') is not None or request.args.get('letters') is not None:
        response = redirect(f"./{utils.genname_letters()}", code=302)
        response.set_cookie("prefer_words_redirect", value="", expires=0)
        return response
    if request.cookies.get("prefer_words_redirect"):
        return redirect(f"./{utils.genname_words()}", code=302)
    return redirect(f"./{utils.genname_letters()}", code=302)


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
    if room.endswith(".md"):
        return
    if room in PROTECTED_PAGES and not ('pass' in message and message['pass'] == INTERNAL_KEY):
        return
    cur = get_db().cursor()
    if len(message['text']) < PAGE_MAX_LENGTH:
        cur.execute("insert or replace into pages values(?, ?);", (message['page'], message['text']))
        get_db().commit()  # 这个阻塞吗？
        emit("text_broadcast", {"text": message['text']}, to=room, broadcast=True, include_self=False)


if __name__ == "__main__":
    socketio.run(app, allow_unsafe_werkzeug=True)
