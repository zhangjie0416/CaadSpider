from datetime import datetime

from common.models import mysql


def login_check(_dict={}):
    sql = 'select id,username from spider_user where username=%s and password=%s'
    args = [_dict['username'], _dict['password']]
    user = mysql.sql_read(sql, args)
    return user


def insert_user(_dict={}):
    sql = 'insert into spider_user (create_time,username,password,company) values (%s,%s,%s,%s)'
    args = [datetime.now(), _dict['username'], _dict['password'], _dict['company']]
    bool = mysql.sql_write(sql, args)
    return bool


def update_user(_dict={}):
    sql = 'update spider_user set update_time=%s,password=%s where username=%s'
    args = [datetime.now(), _dict['password'], _dict['username']]
    bool = mysql.sql_write(sql, args)
    return bool


def select_versions(_dict={}):
    sql = 'select create_time, version, description from spider_version order by id desc'
    if _dict['version']:
        sql += ' limit 1'
        update_read(_dict['username'])
    versions = mysql.sql_read(sql)
    return versions


def select_read(_dict={}):
    sql = 'select is_read from spider_user where username=%s;'
    args = [_dict['username']]
    is_read = mysql.sql_read(sql, args)
    return is_read


def update_read(username):
    sql = 'UPDATE spider_user SET is_read=1 WHERE username=%s'
    args = [username]
    bool = mysql.sql_write(sql, args)
    return bool


def update_session():
    sql = 'update spider_user set is_read=0;truncate table django_session;'
    bool = mysql.sql_write(sql) and '1' or '0'
    return bool
