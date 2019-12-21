from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import time, os, click

# 使用flask模拟一个慢速服务器
app = Flask(__name__)

app.config['SECRET_KEY'] = 'dev'
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
    year = db.Column(db.String(4))  # 电影年份


@app.cli.command()
@click.option('--drop', is_flag=True, help="Create after drop")
def initdb(drop):
    """Initialize the database."""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')  # 输出提示信息


# flask 默认启用多线程
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':  # 判断是post请求
        # 获取表单
        title = request.form.get('title')  # 传入表单对应输入字段的name值
        year = request.form.get('year')
        # 验证数据
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.')  # 显示错误提示
            return redirect(url_for('index'))  # 重定向回主页
        # 数据正确，保存表单数据到数据库
        movie = Movie(title=title, year=year)
        db.session.add(movie)
        db.session.commit()
        flash('Item Created')  # 显示成功创建的提示
        return redirect(url_for('index'))  # 重定向到主页

    # 使用get请求返回的数据
    user = User.query.first()
    movies = Movie.query.all()
    # return '<h1>欢迎来到我的watchlist！</h1> <img src="http://helloflask.com/totoro.gif" >'
    # user = User.query.first()  # 读取用户记录
    # movies = Movie.query.all()  # 读取所有电影记录
    return render_template('index.html', user=user, movies=movies)


# 定义一个编辑电影条目的函数
@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    if request.method == 'POST':
        title = request.form.get('title')
        year = request.form.get('year')

        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=movie_id))
        movie.title = title  # 更新标题
        movie.year = year  # 更新年份
        db.session.commit()  # 提交数据库记录
        flash('Item updated.')
        return redirect(url_for('index'))  # 重定向到主页
    # 以 get请求来获取数据
    return render_template('edit.html', movie=movie)  # 传入被编辑的电影记录


# 删除电影条目
@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)  # 删除电影条目
    db.session.commit()  # 提交到数据库
    flash('Item deleted.')
    return redirect(url_for('index'))  # 重定向到主页


@app.cli.command()
def forge():
    """Generate fake data."""
    db.create_all()

    # 全局的两个变量移动到这个函数内
    name = 'Grey Li'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]

    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)

    db.session.commit()
    click.echo('Done.')


@app.errorhandler(404)
def page_not_found(e):
    user = User.query.first()
    return render_template('404.html', user=user), 404  # 返回模板和状态码


# 定义一个上下文处理函数，存放全局变量，返回的变量可以直接在模板中使用
@app.context_processor
def inject_user():
    user = User.query.first()
    movies = Movie.query.all()
    return dict(user=user, movies=movies)


# return {'user': user,
#         'movies': movies}


if __name__ == '__main__':
    app.run()
