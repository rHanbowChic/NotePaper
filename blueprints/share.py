from flask import render_template
from flask import g
from flask import redirect
import utils.text.link
import utils.text.sanitizer
import utils.router
import utils.member.text2resp
import sqlite3
import os
import hashlib
import base64
from flask import Blueprint
from config.defaults import *

share = Blueprint('share', __name__)

MODULE_DATABASE = os.path.join(os.path.dirname(__file__), "data/share_id.sqlite")
MAIN_DATABASE = "data/note_paper.sqlite"


def gen_share_id(page_id, salt):
    sha = hashlib.sha256()
    sha.update((page_id + salt).encode("utf-8"))
    return base64.urlsafe_b64encode(sha.digest()).decode("utf-8")[:7]

@share.before_request
def before_request():
    g.mdb = sqlite3.connect(MODULE_DATABASE)
    g.db = sqlite3.connect(MAIN_DATABASE)

@share.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()
    mdb = getattr(g, 'mdb', None)
    if mdb is not None:
        mdb.close()


@share.route("/", methods=['GET'])
def root_notice():
    return render_template("paper.html", body="share_explained", site_name=SITE_NAME)


@share.route("/make/<page_id>", methods=['GET'])
def make_share_id_then_redirect(page_id):
    share_id = gen_share_id(page_id, SHARE_ID_HASH_SALT)
    cur = g.mdb.cursor()
    cur.execute("insert or replace into share_id values(?, ?);", (share_id, page_id))
    g.mdb.commit()
    return redirect(f"../{share_id}")

@share.route("/<share_id>")
def shared_page_get(share_id):
    cur = g.db.cursor()
    mcur = g.mdb.cursor()
    if share_id.endswith(".md"):  # /example1.md
        # 返回一个静态客户端，从md_api获取文本并进行前端渲染。（templates/md_client.j2）
        return render_template("paper.html", body="md_client", site_name=SITE_NAME)
    else:  # 如果不以.md结尾，则返回笔记页面。（templates/note.j2）
        target = mcur.execute("select target from share_id where id = ?", (share_id,)).fetchall()
        if len(target) == 0:
            target = ""
        else:
            target = target[0][0]
        text = cur.execute("select text from pages where id = ?", (target,)).fetchall()
        if len(text) == 0:
            text = ""
        else:
            text = text[0][0]

        return utils.member.text2resp.text2resp(share, share_id, text, SITE_NAME, 'share_note')
