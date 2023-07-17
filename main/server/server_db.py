import datetime

from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Text
from sqlalchemy.orm import mapper, sessionmaker


class ServerPool:
    '''
    Класс - оболочка для работы с базой данных сервера.
    Использует SQLite базу данных, реализован с помощью
    SQLAlchemy ORM и используется классический подход.
    '''
    class AllUsers:
        '''Класс - отображение таблицы всех пользователей.'''
        def __init__(self, username, passwd_hash):
            self.name = username
            self.last_login = datetime.datetime.now()
            self.passwd_hash = passwd_hash
            self.pubkey = None
            self.id = None

    class ActiveUsers:
        '''Класс - отображение таблицы активных пользователей.'''
        def __init__(self, user_id, ip_addr, port, login_time):
            self.user = user_id
            self.ip_addr = ip_addr
            self.port = port
            self.login_time = login_time
            self.id = None

    class LoginHistory:
        '''Класс - отображение таблицы истории входов.'''
        def __init__(self, name, date, ip_addr, port):
            self.id = None
            self.name = name
            self.date_time = date
            self.ip_addr = ip_addr
            self.port = port

    class UsersContacts:
        '''Класс - отображение таблицы контактов пользователей.'''
        def __init__(self, user, contact):
            self.id = None
            self.user = user
            self.contact = contact

    class UsersHistory:
        '''Класс - отображение таблицы истории действий.'''
        def __init__(self, user):
            self.id = None
            self.user = user
            self.sent = 0
            self.accepted = 0

    def __init__(self, path):
        self.db_engine = create_engine(
            f'sqlite:///{path}',
            echo=False,
            pool_recycle=7200,
            connect_args={
                'check_same_thread': False})
        self.metadata = MetaData()
        users_table = Table('Users', self.metadata,
                            Column('id', Integer, primary_key=True),
                            Column('name', String, unique=True),
                            Column('last_login', DateTime),
                            Column('passwd_hash', String),
                            Column('pubkey', Text)
                            )
        active_users_table = Table(
            'Active_users', self.metadata, Column(
                'id', Integer, primary_key=True), Column(
                'user', ForeignKey('Users.id'), unique=True), Column(
                'ip_addr', String), Column(
                    'port', Integer), Column(
                        'login_time', DateTime))
        user_login_history = Table('Login_history', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('name', ForeignKey('Users.id')),
                                   Column('date_time', DateTime),
                                   Column('ip_addr', String),
                                   Column('port', String)
                                   )
        contacts = Table('Contacts', self.metadata,
                         Column('id', Integer, primary_key=True),
                         Column('user', ForeignKey('Users.id')),
                         Column('contact', ForeignKey('Users.id'))
                         )
        users_history_table = Table('History', self.metadata,
                                    Column('id', Integer, primary_key=True),
                                    Column('user', ForeignKey('Users.id')),
                                    Column('sent', Integer),
                                    Column('accepted', Integer)
                                    )
        self.metadata.create_all(self.db_engine)
        mapper(self.AllUsers, users_table)
        mapper(self.ActiveUsers, active_users_table)
        mapper(self.LoginHistory, user_login_history)
        mapper(self.UsersContacts, contacts)
        mapper(self.UsersHistory, users_history_table)
        Session = sessionmaker(bind=self.db_engine)
        self.session = Session()
        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    def user_login(self, username, ip_addr, port, key):
        '''
        Метод выполняющийся при входе пользователя, записывает в базу факт входа
        Обновляет открытый ключ пользователя при его изменении.
        '''
        result = self.session.query(self.AllUsers).filter_by(name=username)
        if result.count():
            user = result.first()
            user.last_login = datetime.datetime.now()
            if user.pubkey != key:
                user.pubkey = key
        else:
            raise ValueError('Пользователь не зарегистрирован')
        new_activ_user = self.ActiveUsers(
            user.id, ip_addr, port, datetime.datetime.now())
        self.session.add(new_activ_user)
        history = self.LoginHistory(
            user.id, datetime.datetime.now(), ip_addr, port)
        self.session.add(history)
        self.session.commit()

    def add_user(self, name, passwd_hash):
        '''
        Метод регистрации пользователя.
        Принимает имя и хэш пароля, создаёт запись в таблице статистики.
        '''
        user = self.AllUsers(name, passwd_hash)
        self.session.add(user)
        self.session.commit()
        history_user = self.UsersHistory(user.id)
        self.session.add(history_user)
        self.session.commit()

    def remove_user(self, name):
        '''Метод удаляющий пользователя из базы.'''
        user = self.session.query(self.AllUsers).filter_by(name=name).first()
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()
        self.session.query(self.LoginHistory).filter_by(name=user.id).delete()
        self.session.query(self.UsersContacts).filter_by(user=user.id).delete()
        self.session.query(self.UsersHistory).filter_by(user=user.id).delete()
        self.session.query(self.AllUsers).filter_by(name=name).delete()
        self.session.commit()

    def get_hash(self, name):
        '''Метод получения хэша пароля пользователя.'''
        user = self.session.query(self.AllUsers).filter_by(name=name).first()
        return user.passwd_hash

    def get_pubkey(self, name):
        '''Метод получения публичного ключа пользователя.'''
        user = self.session.query(self.AllUsers).filter_by(name=name).first()
        return user.pubkey

    def check_user(self, name):
        '''Метод проверяющий существование пользователя.'''
        if self.session.query(self.AllUsers).filter_by(name=name).count():
            return True
        else:
            return False

    def user_logout(self, user_name):
        '''Метод фиксирующий отключения пользователя.'''
        user = self.session.query(
            self.AllUsers).filter_by(
            name=user_name).first()
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()
        self.session.commit()

    def process_message(self, sender, recipient):
        '''Метод записывающий в таблицу статистики факт передачи сообщения.'''
        sender = self.session.query(
            self.AllUsers).filter_by(
            name=sender).first().id
        recipient = self.session.query(
            self.AllUsers).filter_by(
            name=recipient).first().id
        sender_row = self.session.query(
            self.UsersHistory).filter_by(
            user=sender).first()
        sender_row.sent += 1
        recipient_row = self.session.query(
            self.UsersHistory).filter_by(
            user=recipient).first()
        recipient_row.accepted += 1
        self.session.commit()

    def add_contact(self, user, contact):
        '''Метод добавления контакта для пользователя.'''
        user = self.session.query(self.AllUsers).filter_by(name=user).first()
        contact = self.session.query(
            self.AllUsers).filter_by(
            name=contact).first()
        if not contact or self.session.query(
                self.UsersContacts).filter_by(
                user=user.id,
                contact=contact.id).count():
            return
        contact_row = self.UsersContacts(user.id, contact.id)
        self.session.add(contact_row)
        self.session.commit()

    def remove_contact(self, user, contact):
        '''Метод удаления контакта пользователя.'''
        user = self.session.query(self.AllUsers).filter_by(name=user).first()
        contact = self.session.query(
            self.AllUsers).filter_by(
            name=contact).first()
        if not contact:
            return
        self.session.query(self.UsersContacts).filter(
            self.UsersContacts.user == user.id,
            self.UsersContacts.contact == contact.id).delete()
        self.session.commit()

    def users_list(self):
        '''Метод возвращающий список известных пользователей со временем последнего входа.'''
        query = self.session.query(
            self.AllUsers.name,
            self.AllUsers.last_login,
        )
        return query.all()

    def active_users_list(self):
        '''Метод возвращающий список активных пользователей.'''
        query = self.session.query(
            self.AllUsers.name,
            self.ActiveUsers.ip_addr,
            self.ActiveUsers.port,
            self.ActiveUsers.login_time
        ).join(self.AllUsers)
        return query.all()

    def login_history(self, user_name=None):
        '''Метод возвращающий историю входов.'''
        query = self.session.query(
            self.AllUsers.name,
            self.LoginHistory.date_time,
            self.LoginHistory.ip_addr,
            self.LoginHistory.port,
        ).join(self.AllUsers)
        if user_name:
            query = query.filter(self.AllUsers.name == user_name)
            return query.all()

    def get_contacts(self, user_name):
        '''Метод возвращающий список контактов пользователя.'''
        user = self.session.query(
            self.AllUsers).filter_by(
            name=user_name).one()
        query = self.session.query(
            self.UsersContacts,
            self.AllUsers.name).filter_by(
            user=user.id).join(
            self.AllUsers,
            self.UsersContacts.contact == self.AllUsers.id)
        return [contact[1] for contact in query.all()]

    def message_history(self):
        '''Метод возвращающий статистику сообщений.'''
        query = self.session.query(
            self.AllUsers.name,
            self.AllUsers.last_login,
            self.UsersHistory.sent,
            self.UsersHistory.accepted
        ).join(self.AllUsers)
        return query.all()


if __name__ == '__main__':
    test_db = ServerPool('../server_db.db3')
    test_db.user_login('client_1', '192.168.1.1', 7777)
    test_db.user_login('client_2', '192.168.1.2', 8001)
    test_db.user_login('client_3', '192.168.1.2', 8002)
    test_db.user_login('client_4', '192.168.1.2', 8003)
    test_db.user_login('client_5', '192.168.1.2', 8004)
    print(test_db.users_list())
    print(test_db.active_users_list())
    test_db.user_logout('client_1')
    print(test_db.active_users_list())
    test_db.login_history('client_1')
    test_db.add_contact('client_2', 'client_1')
    test_db.add_contact('client_3', 'client_2')
    test_db.add_contact('client_5', 'client_3')
    test_db.remove_contact('client_2', 'client_1')
    test_db.process_message('client_1', 'client_4')
    print(test_db.msg_history())
