from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime
from sqlalchemy.orm import mapper, sessionmaker
from variables import *
import datetime


class ServerPool:
    class AllUsers:
        def __init__(self, username):
            self.name = username
            self.last_login = datetime.datetime.now()
            self.id = None

    class ActiveUsers:
        def __init__(self, user_id, ip_addr, port, login_time):
            self.user = user_id
            self.ip_addr = ip_addr
            self.port = port
            self.login_time = login_time
            self.id = None

    class LoginHistory:
        def __init__(self, name, date, ip_addr, port):
            self.id = None
            self.name = name
            self.date_time = date
            self.ip_addr = ip_addr
            self.port = port

    def __init__(self):
        self.db_engine = create_engine(SERVER_DB, echo=False, pool_recycle=7200)
        self.metadata = MetaData()
        users_table = Table('Users', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String, unique=True),
            Column('last_login', DateTime)
        )
        active_users_table = Table('Active_users', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('user', ForeignKey('Users.id'), unique=True),
            Column('ip_addr', String),
            Column('port', Integer),
            Column('login_time', DateTime)                           
        )
        user_login_history = Table('login_history', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('name', ForeignKey('Users.id')),
            Column('date_time', DateTime),
            Column('ip_addr', String),
            Column('port', String)
        )
        self.metadata.create_all(self.db_engine)
        mapper(self.AllUsers, users_table)
        mapper(self.ActiveUsers, active_users_table)
        mapper(self.LoginHistory, user_login_history)
        Session = sessionmaker(bind=self.db_engine)
        self.session = Session()
        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    def user_login(self, username, ip_addr, port):
        print(username, ip_addr, port)
        result = self.session.query(self.AllUsers).filter_by(name=username)
        if result.count():
            user = result.first()
            user.last_login = datetime.datetime.now()
        else:
            user = self.AllUsers(username)
            self.session.add(user)
            self.session.commit()
        new_activ_user = self.ActiveUsers(user.id, ip_addr, port, datetime.datetime.now())
        self.session.add(new_activ_user)
        history = self.LoginHistory(user.id, datetime.datetime.now(), ip_addr, port)
        self.session.add(history)
        self.session.commit()

    def user_logout(self, user_name):
        user = self.session.query(self.AllUsers).filter_by(name=user_name).first()
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()
        self.session.commit()

    def users_list(self):
        query = self.session.query(
            self.AllUsers.name,
            self.AllUsers.last_login,
        )
        return query.all()
    
    def active_users_list(self):
        query = self.session.query(
            self.AllUsers.name,
            self.ActiveUsers.ip_addr,
            self.ActiveUsers.port,
            self.ActiveUsers.login_time
        ).join(self.AllUsers)
        return query.all()

    def login_history(self, user_name=None):
        query = self.session.query(
            self.AllUsers.name,
            self.LoginHistory.date_time,
            self.LoginHistory.ip_addr,
            self.LoginHistory.port,
        ).join(self.AllUsers)
        if user_name:
            query = query.filter(self.AllUsers.name == user_name)
            return query.all()


if __name__ == '__main__':
    test_db = ServerPool()
    test_db.user_login('client_1', '192.168.1.1', 7777)
    test_db.user_login('client_2', '192.168.1.2', 8001)
    print(test_db.active_users_list())
    test_db.user_logout('client_1')
    print(test_db.active_users_list())
    test_db.login_history('client_1')
    print(test_db.users_list())

