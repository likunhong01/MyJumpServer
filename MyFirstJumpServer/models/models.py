#coding=utf-8
#Version:python3.6.0
#Tools:Pycharm 2017.3.2
# Author:LIKUNHONG
__date__ = '2018/11/1 14:16'
__author__ = 'likunkun'

from sqlalchemy import create_engine,Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String,ForeignKey,UniqueConstraint
from sqlalchemy.orm import relationship
from  sqlalchemy.orm import sessionmaker
from sqlalchemy import or_,and_
from sqlalchemy import func
from sqlalchemy_utils import ChoiceType,PasswordType

Base = declarative_base()

# host_m2m_remoteuser = Table('host_m2m_remoteuser', Base.metadata,
#                             Column('host_id', Integer, ForeignKey('host.id')),
#                             Column('remoteuser_id', Integer, ForeignKey('remote_user.id')))


user_m2m_bindhost = Table('user_m2m_bindhost', Base.metadata,
                          Column('userprofile_id',Integer, ForeignKey('user_profile.id')),
                          Column('bindhost_id',Integer, ForeignKey('bind.id')),
                          )







class Host(Base):
    __tablename__ = 'host'
    id = Column(Integer,primary_key=True)
    hostname = Column(String(64),unique=True)
    ip = Column(String(64), unique=True)
    port = Column(Integer,default=22)   #默认值

    # remote_users = relationship('和哪个类(表）关联',secondary='通过什么表关联', backref='反查')
    remote_users = relationship('RemoteUser',secondary='host_m2m_remoteuser', backref='hosts')
    def __repr__(self):
        return self.hostname


class HostGroup(Base):
    __tablename__ = 'host_group'
    id = Column(Integer,primary_key=True)
    name = Column(String(64), unique=True)  #不唯一
    def __repr__(self):
        return self.name


class RemoteUser(Base):
    __tablename__ = 'remote_user'
    __table_args__ = (UniqueConstraint('auth_type','username','password', name='_user_passwd_uc'),)#联合唯一

    AuthTypes = [
        ('ssh-passwd', 'SSH/Password'), #第一个是真正存到数据库的，第二个是显示给我们看的
        ('ssh-key','SSH/KEY'),
    ]
    id = Column(Integer, primary_key=True)
    auth_type = Column(ChoiceType(AuthTypes))
    username = Column(String(32))
    password = Column(String(128))



class BindHost(Base):
    '''
    实现
    host
    192.168.1.11    web     北京组
    这样的表格
    '''
    __tablename__ = 'bind_host'
    __table_args__ = (UniqueConstraint('host_id','group_id','remoteuser_id', name='_host_group_remoteuser_uc'))#联合唯一

    id = Column(Integer,primary_key=True)
    host_id = Column(Integer,ForeignKey('host.id'))
    group_id = Column(Integer, ForeignKey('group.id'))
    remoteuser_id = Column(Integer, ForeignKey('remote_user.id'))

    host = relationship('Host',backref='bind_hosts')
    host_group = relationship('HostGroup', backref='bind_hosts')
    remote_user = relationship('RemoteUser',backref='bind_hosts')

    def __repr__(self):
        return "%s,%s,%s"%(self.host.id,
                           self.remote_user.username,
                           self.host_group.name)



class UserProfile(Base):
    __tablename__ = 'user_profile'

    id = Column(Integer, primary_key=True)
    username = Column(String(32), unique=True)
    password = Column(String(128))

    bind_hosts = relationship('BindHost',secondary='user_m2m_bindhost',backref='user_profile')