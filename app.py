from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import time, os, click

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)

app.config['SECRET_KEY'] = 'dev'
# 配置数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'data.db')  # 拼接数据库地址，在根目录下创建文件
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
# 在扩展类实例化前加载配置
db = SQLAlchemy(app)  # 初始化扩展，传入程序实例app


class User(db.Model, UserMixin):  # 表名将会是user（自动生成，小写处理）
    id = db.Column(db.Integer, primary_key=True)  # 设置id为主键
    name = db.Column(db.String(20))  # 名字
    username = db.Column(db.String(20))  # 用户名
    password_hash = db.Column(db.String(128))  # 密码散列值

    def set_password(self, password):  # 用来接收传入的密码
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):  # 用于验证密码
        return check_password_hash(self.password_hash, password)


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
        if not current_user.is_authenticated:
            flash("请先登录")
            return redirect(url_for('index'))  # 检测是否登录，未登录就跳转到首页
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
@login_required
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
@login_required  # 登录保护
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

# 编写命令函数 生成管理员账户
@app.cli.command()
@click.option('--username', prompt=True, help="the username used to login.")
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    """Create User"""
    db.create_all()
    user = User.query.first()
    if user is not None:
        click.echo("Updating user...")
        user.username = username
        user.set_password(password)
    else:
        click.echo('Creating user')
        user = User(username=username, name='Admin')
        user.set_password(password)  # 设置密码
        db.session.add(user)
    db.session.commit()  # 将数据提交到数据库
    click.echo('Done.')


login_manager = LoginManager(app)  # 实例化扩展类LoginManager
login_manager.login_view = 'login'
login_manager.login_message = "未登录，请先登录"


@login_manager.user_loader
def load_user(user_id):  # 创建用户加载回调函数，接收用户ID作为参数
    user = User.query.get(int(user_id))  # 用id作为User模型的主键查询对应用户
    return user  # 返回用户对象


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))
        user = User.query.first()
        # 验证用户名和密码是否一致
        if username == user.username and user.validate_password(password):
            login_user(user)  # 登入用户
            flash('Login success')
            return redirect(url_for('index'))  # 重定向到首页
        flash('Invalid username or password')  # 验证失败，显示错误消息
        return redirect(url_for('login'))  # 重新定位到登录页面
    return render_template('login.html')  # 以get请求页面时，展示login界面


@app.route('/logout')
@login_required
def logout():
    logout_user()  # 登出用户
    flash("Goodbye~")
    return redirect(url_for('index'))  # 重定向到首页


@app.route('/settings', methods=['POST', 'GET'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form.get('name')
        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))
        current_user.name = name  # 设置当前用户的用户名为form表格获取到的
        db.session.commit()   # 提交记录到数据库
        flash('Settings updated.')
        return redirect(url_for('index'))
    return render_template('settings.html')


if __name__ == '__main__':
    app.run()
