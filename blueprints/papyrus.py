from urllib.parse import quote_plus

from flask import render_template, request, Response, abort, jsonify
from flask import g
from flask import redirect
import utils
import sqlite3
import os
import hashlib
import base64
from flask import Blueprint
from config import *

papyrus = Blueprint('papyrus', __name__)

MAIN_DATABASE = "data/note_paper.sqlite"

@papyrus.before_request
def before_request():
    g.db = sqlite3.connect(MAIN_DATABASE, timeout=30)
    g.db.execute("PRAGMA journal_mode = WAL")
    g.db.execute("PRAGMA cache_size = -2000")

@papyrus.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@papyrus.route("/version", methods=["GET"])
def version():
    return {
        "major": 1,
        "minor": 6,
        "patch": 0,
    }


@papyrus.route("/file/<id>", methods=["GET"])
def file_get(id):
    cur = g.db.cursor()
    text = utils.sqlite_result_extract(
        cur.execute("select text from pages where id = ?", (id,)).fetchall()
    )
    return jsonify(text)


@papyrus.route("/file/<id>", methods=["POST"])
def file_post(id):
    cur = g.db.cursor()
    if id.endswith(".md") or id in PROTECTED_PAGES:
        abort(403)
    if request.json is None or "text" not in request.json:
        abort(400)
    if len(request.json["text"]) >= PAGE_MAX_LENGTH:
        abort(413)
    cur.execute("insert or replace into pages values(?, ?);", (id, request.json["text"]))
    return {
        "success": True,
    }


@papyrus.route("/markdown/<id>", methods=["GET"])
def md_get(id):
    cur = g.db.cursor()
    text = utils.sqlite_result_extract(
        cur.execute("select text from pages where id = ?", (id,)).fetchall()
    )
    text = utils.auto_link(text)
    text = utils.sanitize_html(text)
    return jsonify(text)


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