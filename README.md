# NotePaper
在线剪贴板服务器。概念源于Note.ms。

## 包含功能
* 复刻了所有 Note.ms 发现的功能
* 无需刷新，实时更新页面，且摆放光标到合适的位置
* 可配置深色主题
* TeX 数学公式支持
* 可选的等宽字体
* 重定向至随机双单词页面（四字母页面仍可用）
* 页面储存于SQLite数据库
* 向Note.ms的完全兼容（脚本无需修改即可使用）
#### 管理特性 （详见config/config.py)
* 自定义NotePaper实例的名称
* 锁定一组受保护页面
* 设置用户初次访问的欢迎页面
* 限制页面文本最大长度

### TeX
NotePaper的md页面支持行内LaTeX数学公式的渲染。公式需要写在两个"$"符号之间。
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

## Docker Compose 部署
拉取项目代码到本地，进入项目代码根目录，根据`config/README.txt`修改项目配置，而后在项目代码根目录执行命令：
```bash
# 启动并后台运行容器
docker-compose up -d
# 停止并删除容器
docker-compose down
```

## 我想放到服务器上，像[note.ect.fyi](https://note.ect.fyi/)
这是一个Flask应用，你可以使用部署任何Flask应用的方式部署它。

例如使用Gunicorn与Nginx。
