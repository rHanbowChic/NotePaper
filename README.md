# NotePaper
在线剪贴板服务器。概念源于Note.ms。

## 包含功能
* 复刻了所有 Note.ms 发现的功能
* 无需刷新，实时更新页面，且摆放光标到合适的位置
* TeX 数学公式支持
* 可选的等宽字体
* 重定向至随机双单词页面（四字母页面仍可用）
* 页面储存于SQLite数据库
* 向Note.ms的完全兼容（脚本无需修改即可使用）

### TeX
在一个开头与结尾均为“$”的行中，可填写LaTeX风格的数学公式。
```markdown
## Fundamental theorem of calculus

$\int_{a}^{b} f'(t) \, dt = f(b) - f(a)$
```

### 等宽字体

在Query string中添加`mono`或`m`参数。

例：`https://notepaper.example.com/my-code-snippet?mono`

### 双单词页面名

访问根目录时，在Query string中添加`words`或`w`参数。

例：`https://notepaper.example.com/?words`

这将跳转到一个名字由2个常见英语单词组成的页面。

## 如何使用？
首先需要一个大于等于3.8版本的Python。在项目根目录下运行
```
py -m pip install -r requirements.txt
py app.py
```
在浏览器访问`127.0.0.1:5000`。Enjoy！

## 我想放到服务器上，像[note.ect.fyi](https://note.ect.fyi/)
这是一个Flask应用，你可以使用部署任何Flask应用的方式部署它。

例如使用Gunicorn与Nginx。
