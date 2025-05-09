from urllib.parse import quote_plus

from flask import render_template, request, Response, abort, jsonify, make_response
from flask import g
from flask import redirect
import utils
import sqlite3
import os
import hashlib
import base64
from flask import Blueprint
from config import *

from .share import gen_share_id

papyrus = Blueprint('papyrus', __name__)

MAIN_DATABASE = "data/note_paper.sqlite"
SHARE_DATABASE = os.path.join(os.path.dirname(__file__), "data/share_id.sqlite")

def text_resp_dic(text: str):
    return {
        "text": text,
    }

@papyrus.before_request
def before_request():
    g.db = sqlite3.connect(MAIN_DATABASE, timeout=30)
    g.db.execute("PRAGMA journal_mode = WAL")
    g.db.execute("PRAGMA cache_size = -2000")
    if USE_SHARE:
        g.share_db = sqlite3.connect(SHARE_DATABASE, timeout=30)

@papyrus.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()
    db = getattr(g, 'share_db', None)
    if db is not None:
        db.close()


@papyrus.route("/info", methods=["GET"])
def info():
    return {
        "version": {
            "major": 1,
            "minor": 6,
            "patch": 0,
        },
        "site_config": {
            "site_name": SITE_NAME,
            "page_max_length": PAGE_MAX_LENGTH,
            "allow_js_markdown_links": ALLOW_JS_MARKDOWN_LINKS,
            "show_welcome": SHOW_WELCOME,
            "welcome_page": WELCOME_PAGE,
            "use_share": USE_SHARE,
        },

    }


@papyrus.route("/file/<id>", methods=["GET"])
def file_get(id):
    cur = g.db.cursor()
    text = utils.sqlite_result_extract(
        cur.execute("select text from pages where id = ?", (id,)).fetchall()
    )
    return text_resp_dic(text)


@papyrus.route("/file/<id>", methods=["POST"])
def file_post(id):
    cur = g.db.cursor()
    if id.endswith(".md") or id in PROTECTED_PAGES:
        return jsonify({"success": False}), 403
    if request.json is None or "text" not in request.json:
        return jsonify({"success": False}), 400
    if len(request.json["text"]) >= PAGE_MAX_LENGTH:
        return jsonify({"success": False}), 413
    cur.execute("insert or replace into pages values(?, ?);", (id, request.json["text"]))
    g.db.commit()
    return {"success": True}


@papyrus.route("/markdown/<id>", methods=["GET"])
def md_get(id):
    cur = g.db.cursor()
    text = utils.sqlite_result_extract(
        cur.execute("select text from pages where id = ?", (id,)).fetchall()
    )
    text = utils.auto_link(text)
    text = utils.sanitize_html(text)
    return text_resp_dic(text)


@papyrus.route("/saving/<ext>/<id>", methods=["GET"])
def saving_get(ext, id):
    if ext not in ["txt", "md"]:
        abort(400)
    cur = g.db.cursor()
    text = utils.sqlite_result_extract(
        cur.execute("select text from pages where id = ?", (id,)).fetchall()
    )
    return Response(text, mimetype='text/plain',
                    headers={"Content-disposition": f"attachment; filename*=UTF-8''{quote_plus(id)}.{ext}"})


if USE_SHARE:
    def get_text_from_sid(sid):
        target = get_target_from_sid(sid)
        cur = g.db.cursor()
        text = utils.sqlite_result_extract(
            cur.execute("select text from pages where id = ?", (target,)).fetchall()
        )
        return text

    def get_target_from_sid(sid):
        scur = g.share_db.cursor()
        target = utils.sqlite_result_extract(
            scur.execute("select target from share_id where id = ?", (sid,)).fetchall()
        )
        return target

    @papyrus.route("/file/s/<sid>", methods=["GET"])
    def shared_file_get(sid):
        text = get_text_from_sid(sid)
        return text_resp_dic(text)

    @papyrus.route("/markdown/s/<sid>", methods=["GET"])
    def shared_md_get(sid):
        text = get_text_from_sid(sid)
        text = utils.auto_link(text)
        text = utils.sanitize_html(text)
        return text_resp_dic(text)


    @papyrus.route("/saving/<ext>/s/<sid>", methods=["GET"])
    def shared_saving_get(ext, sid):
        if ext not in ["txt", "md"]:
            abort(400)
        text = get_text_from_sid(sid)
        return Response(text, mimetype='text/plain',
                        headers={"Content-disposition": f"attachment; filename*=UTF-8''{quote_plus(sid)}.{ext}"})

    @papyrus.route("/share-id/<page_id>", methods=["GET"])
    def share_id_get(page_id):
        real_id = gen_share_id(page_id, SHARE_ID_HASH_SALT)
        scur = g.share_db.cursor()
        id_exists = len(scur.execute("select target from share_id where id = ?", (real_id,)).fetchall())
        return {
            "share_id": real_id if id_exists else None
        }

    @papyrus.route("/share-id/<page_id>", methods=["POST"])
    def share_id_post(page_id):
        share_id = gen_share_id(page_id, SHARE_ID_HASH_SALT)
        scur = g.share_db.cursor()
        scur.execute("insert or replace into share_id values(?, ?);", (share_id, page_id))
        g.share_db.commit()
        return {"success": True, "share_id": share_id}