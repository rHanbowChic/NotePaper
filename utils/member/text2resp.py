from urllib.parse import quote_plus
from flask import Response, render_template, request
import utils


def text2resp(app, page, text, site_name, template):
    is_text_request = request.args.get('text') is not None or request.args.get('t') is not None
    is_md_api_request = request.args.get('md_api') is not None

    if (request.headers.get("User-Agent") is not None and (
            "curl" in request.headers.get("User-Agent")
            or "Wget" in request.headers.get("User-Agent")
            or is_text_request
    )):  # 给带有text参数的请求始终直接显示内容
        return Response(text, mimetype='text/plain')

    elif is_md_api_request:
        text = utils.text.link.auto_link(text)
        text = utils.text.sanitizer.sanitize_html(text)
        return Response(text, mimetype='text/plain')

    elif request.args.get('save') is not None:
        return Response(text, mimetype='text/plain',
                        headers={"Content-disposition": f"attachment; filename*=UTF-8''{quote_plus(page)}.txt"})

    else:
        return render_template(template, page=page, text=text, site_name=site_name)
