# 这是NotePaper的默认配置文件。不要修改此文件！每次Git拉取它都会被覆盖。
# 不要修改此文件！
# 创建一个config.py并将其作为配置文件。
import os

# 站点名字。您可能会想更改它。
SITE_NAME = "NotePaper"

# 页面文本的最大长度。超出此长度将不会保存。（设置为0可以全域只读）
PAGE_MAX_LENGTH = 100000

# 是否允许javascript协议出现在markdown链接中。
ALLOW_JS_MARKDOWN_LINKS = True

# 是否为初次来访者显示欢迎页面。
SHOW_WELCOME = False

# 欢迎页面。如果启用SHOW_WELCOME，这个页面应该位于PROTECTED_PAGES中，原因不言自明。
WELCOME_PAGE = "welcome"

# 内部密钥。修改受保护页面时需要使用它。例：page?pass=123
# 为了安全性，请尽量使用10位以上的随机密码，并在浏览器隐私模式下进行编辑。
INTERNAL_KEY = "!changeme!"

# 受保护的页面列表。它们对用户是只读的。
PROTECTED_PAGES = (

)

# 是否在/s/目录启用只读分享功能。
USE_SHARE = False

# import secrets, base64; print(base64.b64encode(secrets.token_bytes(18)))  # 在Python shell中运行以获取随机盐值
SHARE_ID_HASH_SALT = "exampleX3lMgI0MbaU5mtB"



if os.path.isfile(os.path.join(os.path.dirname(__file__), "config.py")):
    from .config import *  # PyCharm可能会对这一句报错，但属正常。只需要忽略它。
