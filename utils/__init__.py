from .router import genname_letters, genname_words

from .member.text2resp import text2resp

from .init_db import init_notepaper_db

from .text.link import auto_link

from .text.sanitizer import sanitize_html


def sqlite_result_extract(result):
    if len(result) == 0:
        text = ""
    else:
        text = result[0][0]
    return text
