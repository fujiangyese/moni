from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import time, os,click

# 使用flask模拟一个慢速服务器
app = Flask(__name__)

# 配置数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'data.db')  # 拼接数据库地址，在根目录下创建文件
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
# 在扩展类实例化前加载配置
db = SQLAlchemy(app)  # 初始化扩展，传入程序实例app


class User(db.Model):  # 表名将会是user（自动生成，小写处理）
    id = db.Column(db.Integer, primary_key=True)  # 设置id为主键
    name = db.Column(db.String(20))  # 名字


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))  # 电影标题
    yaer = db.Column(db.String(4))  # 电影年份


# flask 默认启用多线程
@app.route('/')
def index():
    # return '<h1>欢迎来到我的watchlist！</h1> <img src="http://helloflask.com/totoro.gif" >'
    return render_template("index.html", name=name, movies=movie)


# 准备一些数据
name = "Grey Li"
movie = [
    {"title": "My world", "year": 2019},
    {"title": "My world", "year": 2019},
    {"title": "My world", "year": 2019},
    {"title": "My world", "year": 2019},
    {"title": "My world", "year": 2019},
    {"title": "My world", "year": 2019},
]

if __name__ == '__main__':
    app.run()
