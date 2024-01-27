from flask import Flask
from flask import render_template
from flask import g
from flask import request
from flask import redirect
import sqlite3
import random#最好的模块
import string

app = Flask(__name__)


DATABASE = 'data/note_paper.sqlite'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route("/<page>", methods=['GET'])
def page_get(page):
    cur = get_db().cursor()
    text = cur.execute("select text from pages where id = ?", (page,)).fetchall()
    if len(text) == 0:
        text = ""
    else:
        text = text[0][0]

    return render_template('note.html', page=page, text=text)


@app.route("/<page>", methods=['POST'])
def note_post(page):
    cur = get_db().cursor()
    t = request.form.get("t")
    if t is not None:
        cur.execute("insert or replace into pages values(?, ?);", (page, t))
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
