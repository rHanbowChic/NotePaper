import re  # 最坏的模块


def auto_link(passage: str):
    """为所有HTTP，HTTPS与站内链接URL自动添加Markdown超链接。"""
    pat_internal = r"\s(\/\w+[^=\s]*)"  # 极度不适
    passage = re.sub(pat_internal, r'[\1](\1)', passage)
    pat_external = r"(https?:\/\/\w+\.\w+[^=\s]*)"  # 令人失去理智的古老咒文
    return re.sub(pat_external, r'[\1](\1)', passage)


if __name__ == "__main__":
    print(auto_link("Please keep in mind that /Google is your friend. Always. Just check https://www.google.com/ then you'll actually know EVERYTHING of the universe."))

