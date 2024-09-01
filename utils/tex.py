import base64
import matplotlib.pyplot as plt
import io

MAX_RENDERING_AMOUNT = 30  # 每个页面中最大可渲染的TeX数量
MAX_TEX_LENGTH = 100  # 每个TeX的最大允许长度（超出则不会渲染）


def latex_to_data_url(tex):
    """将一个标准的LaTeX数学公式转换为SVG图像的data URL。"""
    buf = io.BytesIO()

    fig = plt.figure(figsize=(3, 0.5))
    text = fig.text(
        x=0.5,
        y=0.5,
        s=f"{tex}",
        horizontalalignment="center",
        verticalalignment="center",
        fontsize=16,
    )
    try:  # 我不知道类似于\some\unwanted\stuff\here\\\\aaa?:"{{:的东西为什么会在这一步出现ValueError，但它确实如此
        bbox = fig.texts[0].get_window_extent()
    except ValueError:
        return "data:image/svg+xml;base64,"
    img_size = (bbox.width / 100, bbox.height / 100 + 0.1)
    fig.set_size_inches(img_size)

    plt.savefig(buf, format="png")

    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")


def tex_to_markdown(passage: str):
    """将一段文字中所有以$$包围的TeX行替换为Markdown格式的data URL。"""
    lines = passage.split("\n")
    attempts = 0  # 防止大量TeX卡崩服务器
    for idx, line in enumerate(lines):
        if line.startswith("$") and line.endswith("$") and attempts < MAX_RENDERING_AMOUNT and len(line) < MAX_TEX_LENGTH:
            lines[idx] = f"![{line}]({latex_to_data_url(line)})"
            attempts += 1
    return "\n".join(lines)


if __name__ == "__main__":  # 测试测试
    print(latex_to_data_url(r"$\frac{-e^{i\pi}}{2^n}$"))

