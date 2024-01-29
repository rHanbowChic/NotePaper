from flask import Flask
from flask import render_template
from flask import g
from flask import request
from flask import redirect
from flask import Response
from flaskext.markdown import Markdown
from bs4 import BeautifulSoup
from zlib import crc32
import sqlite3
import random#最好的模块
import string

app = Flask(__name__)
Markdown(app)


DATABASE = 'data/note_paper.sqlite'


VALID_TAGS = ['strong', 'em', 'p', 'ul', 'li', 'br', 'sub', 'sup', 'ruby', 'rt', 'rp', 'details', 'summary']


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
        is_hash_request = request.args.get('request_hash') is not None
        if is_hash_request:
            crc32_hash = cur.execute("SELECT hash FROM pages WHERE id = ?", (page,)).fetchall()
            if len(crc32_hash) == 0:
                crc32_hash = ""
            else:
                crc32_hash = crc32_hash[0][0]
            return Response(str(crc32_hash), mimetype='text/plain')
        else:
            text = cur.execute("select text from pages where id = ?", (page,)).fetchall()
            if len(text) == 0:
                text = ""
            else:
                text = text[0][0]

            is_text_request = request.args.get('request_text') is not None
            if (request.headers.get("User-Agent") is not None and (
                "curl/" in request.headers.get("User-Agent")
                or "Wget/" in request.headers.get("User-Agent")
                or is_text_request
            )):  # 给带有request_text参数的请求始终直接显示内容，用于Ajax实时更新
                return Response(text, mimetype='text/plain')
            else:
                return render_template('note.html', page=page, text=text)


@app.route("/<page>", methods=['POST'])
def note_post(page):
    cur = get_db().cursor()
    # 正常情况下，浏览器永远不会对以.md结尾的页面发送POST请求。但不排除使用其他程序的情况。
    if not page.endswith(".md"):
        t = request.form.get("t")
        if t is not None:
            crc32_hash = crc32(bytes(t, 'utf-8'))
            cur.execute("insert or replace into pages values(?, ?, ?);", (page, t, crc32_hash))
            get_db().commit()
    return ""


@app.route("/", methods=['GET'])
def root_redirect():
    randword = ""
    for i in range(0, 4):
        randword += random.choice(string.ascii_lowercase)
    return redirect(f"./{randword}", code=302)


if __name__ == "__main__":
    app.run()
