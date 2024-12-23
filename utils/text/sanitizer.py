from bs4 import BeautifulSoup
import re
# import nh3


VALID_TAGS = ['strong', 'em', 'p', 'ul', 'ol', 'li', 'b', 'i',
              'br', 'sub', 'sup', 'ruby', 'rt', 'rp', 'details', 'summary', 's',
              'marquee', 'style', 'div', 'span']

VALID_ATTRS = ['class', 'style']


def sanitize_html(text, remove_js_links = False):
    """通过删除标签和属性，去除段落中可能的XSS代码。"""
    # 这是BeautifulSoup。
    soup = BeautifulSoup(text, "html.parser")
    # 遍历所有HTML标签，如果在VALID_TAGS中，则保留标签但删除所有属性（防止诸如onclick等属性的脚本执行）
    # 如果不在，则删除标签（在hidden设置为True时输出文本）
    for tag in soup.findAll(True):
        if tag.name in VALID_TAGS:
            lst = []
            for attr in tag.attrs:
                lst.append(attr)
            for attr in lst:
                if attr not in VALID_ATTRS:
                    del tag[attr]
        else:
            tag.hidden = True
    if remove_js_links:
        return remove_javascript_protocol_markdown_links(soup.renderContents().decode('utf-8'))
    return soup.renderContents().decode('utf-8')


def remove_javascript_protocol_markdown_links(text):
    pattern = r'\[.*?\]\(javascript:.*\)'

    while re.search(pattern, text, re.IGNORECASE):
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    return text


# NH3_ALLOWED_TAGS = nh3.ALLOWED_TAGS | {"style"}
# nh3底层的Rust库ammonia确实支持自定义黑名单，但nh3似乎没有把这个函数包装上去！“style”正好在黑名单里。悲剧...


"""
def sanitize_using_nh3(text):
    return nh3.clean(text)
"""


if __name__ == '__main__':
    print(sanitize_html("""
[Normal link](https://example.com)
[JavaScript link](JavaScript:alert('XSS'))
Another line with [JAVASCRIPT link](JAVASCRIPT:console.log('test')) and [another one](JavaScript:void(0))
""", remove_js_links=True))