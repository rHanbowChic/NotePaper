# NotePaper
开源 Note.ms 服务器，使用 Flask 与 SQLite 作为后端。

## 如何使用？
首先需要一个大于等于3.8版本的Python。在项目根目录下运行
```
py -m pip install -r requirements.txt
py app.py
```
在浏览器访问`127.0.0.1:5000`。Enjoy！

## 我想放到服务器上，像[knockoff](https://knockoff.ect.fyi/)
这是一个Flask应用，你可以使用部署任何Flask应用的方式部署它。

例如使用Gunicorn与Nginx。

<sup><sub>~~我想我和纸干上了~~</sub></sup>

## 目前的任务
* 使用 WebSocket 重写
  * 考虑到加入实时更新后，这里已经不再是 Ajax 的长处。一秒发送一次请求使服务器日志成为动辄几十MB的怪兽级别
