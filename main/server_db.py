from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime
from sqlalchemy.orm import mapper, sessionmaker
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

    class UsersContacts:
        def __init__(self, user, contact):
            self.id = None
            self.user = user
            self.contact = contact


    class UsersHistory:
        def __init__(self, user):
            self.id = None
            self.user = user
            self.sent = 0
            self.accepted = 0


    def __init__(self, path):
        self.db_engine = create_engine(f'sqlite:///{path}', echo=False, pool_recycle=7200, connect_args={'check_same_thread': False})
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
        users_hist_tbl = Table('History', self.metadata,
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
        mapper(self.UsersHistory, users_hist_tbl)
        Session = sessionmaker(bind=self.db_engine)
        self.session = Session()
        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    def user_login(self, username, ip_addr, port):
        result = self.session.query(self.AllUsers).filter_by(name=username)
        if result.count():
            user = result.first()
            user.last_login = datetime.datetime.now()
        else:
            user = self.AllUsers(username)
            self.session.add(user)
            self.session.commit()
            user_in_hist = self.UsersHistory(user.id)
            self.session.add(user_in_hist)
        new_activ_user = self.ActiveUsers(user.id, ip_addr, port, datetime.datetime.now())
        self.session.add(new_activ_user)
        history = self.LoginHistory(user.id, datetime.datetime.now(), ip_addr, port)
        self.session.add(history)
        self.session.commit()

    def user_logout(self, user_name):
        user = self.session.query(self.AllUsers).filter_by(name=user_name).first()
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()
        self.session.commit()

    def process_message(self, sender, recipient):
        sender = self.session.query(self.AllUsers).filter_by(name=sender).first().id
        recipient = self.session.query(self.AllUsers).filter_by(name=recipient).first().id
        sender_row = self.session.query(self.UsersHistory).filter_by(user=sender).first()
        sender_row.sent += 1
        recipient_row = self.session.query(self.UsersHistory).filter_by(user=recipient).first()
        recipient_row.accepted += 1
        self.session.commit()

    def add_contact(self, user, contact):
        user = self.session.query(self.AllUsers).filter_by(name=user).first()
        contact = self.session.query(self.AllUsers).filter_by(name=contact).first()
        if not contact or self.session.query(self.UsersContacts).filter_by(user=user.id, contact=contact.id).count():
            return
        contact_row = self.UsersContacts(user.id, contact.id)
        self.session.add(contact_row)
        self.session.commit()

    def remove_contact(self, user, contact):
        user = self.session.query(self.AllUsers).filter_by(name=user).first()
        contact = self.session.query(self.AllUsers).filter_by(name=contact).first()
        if not contact:
            return
        self.session.query(self.UsersContacts).filter(
            self.UsersContacts.user == user.id,
            self.UsersContacts.contact == contact.id).delete()
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
        
    def get_contacts(self, user_name):
        user = self.session.query(self.AllUsers).filter_by(name=user_name).one()
        query = self.session.query(self.UsersContacts, self.AllUsers.name).filter_by(user=user.id).join(self.AllUsers,\
        self.UsersContacts.contact == self.AllUsers.id)
        return [contact[1] for contact in query.all()]

    def msg_history(self):
        query = self.session.query(
            self.AllUsers.name,
            self.AllUsers.last_login,
            self.UsersHistory.sent,
            self.UsersHistory.accepted
        ).join(self.AllUsers) 
        return query.all()   
        


if __name__ == '__main__':
    test_db = ServerPool()
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

