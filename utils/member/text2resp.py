from urllib.parse import quote_plus
from flask import Response, render_template, request
from ..text import link, sanitizer
from config import *


def text2resp(app, page, text, site_name, body):
    is_text_request = request.args.get('text') is not None or request.args.get('t') is not None

    if (request.headers.get("User-Agent") is not None and (
            "curl" in request.headers.get("User-Agent")
            or "Wget" in request.headers.get("User-Agent")
            or is_text_request
    )):  # 给带有text参数的请求始终直接显示内容
        return Response(text, mimetype='text/plain')

    else:
        return render_template("paper.html", body=body, page=page, text=text, site_name=site_name)
