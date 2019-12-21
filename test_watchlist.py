import unittest
from app import app, db, Movie, User


class WatchlistTestCase(unittest.TestCase):
    def setUp(self) -> None:
        app.config.update(TESTING=True,
                          SQLALCHEMY_DATABASE_URI='sqlite:////:memory:')
        # 创建数据库和表
        db.create_all()
        # 创建测试数据，一个用户，一条电影条目
        user = User(name='Test', username='test')
        user.set_password('123')
        movie = Movie(title='Test Movie Title', year='2019')
        # 使用add_all()方法，一次性添加多个实例
        db.session.add_all([user, movie])
        db.session.commit()



    def tearDown(self) -> None:
        pass
