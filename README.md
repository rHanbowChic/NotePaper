# NotePaper
开源 Note.ms 服务器，使用 Flask 与 SQLite 作为后端。

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

## 目前的任务
* 每次文本更新后，光标都会移到最后。
  * 更新后，光标应该插入到对用户最友好的位置。
------

NotePaper使用WebSocket更新笔记内容，但接受带有t参数的HTTP POST。

<sup><sub>~~我想我和纸干上了~~</sub></sup>
