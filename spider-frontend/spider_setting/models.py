from datetime import datetime

from common.models import mysql
from spider.settings import SPIDER_URLS, SPIDER_DATA


def select_setting(_dict={}):
    sql = '''
        SELECT
            a.is_full,
            a.group_name,
            a.task_name,
            a.first_urls,
            a.first_url,
            a.urls_xpath,
            a.second_url,
            a.data_xpath,
            a.is_example,
            a.timer,
            b.username
        FROM
            spider_setting a 
            JOIN spider_user b ON b.id=a.user_id
        WHERE
            a.id =%s
    '''
    args = [_dict['id']]
    setting = mysql.sql_read(sql, args)
    return setting


def update_setting(_dict={}):
    sql = '''
            UPDATE spider_setting
            SET update_time =%s,
            group_name =%s,
            task_name =%s,
            first_urls =%s,
            first_url =%s,
            urls_xpath =%s,
            second_url =%s,
            data_xpath =%s,
            timer =%s,
            is_full =%s
            WHERE
                id =%s
                AND user_id =%s
        '''
    args = [datetime.now(), _dict["group_name"], _dict['task_name'], _dict["first_urls"], _dict["first_url"],
            _dict["urls_xpath"], _dict["second_url"], _dict["data_xpath"], _dict["timer"], _dict["is_full"], _dict["id"], _dict['user_id']]
    bool = mysql.sql_write(sql, args)
    return bool


def insert_setting(_dict={}):
    create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sql = '''
        INSERT INTO spider_setting (create_time, group_name, task_name, first_urls,first_url, urls_xpath,second_url, data_xpath, is_example, user_id, timer, is_full)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    '''
    args = [create_time, _dict["group_name"], _dict['task_name'], _dict["first_urls"], _dict["first_url"], _dict["urls_xpath"], _dict["second_url"],
            _dict["data_xpath"], _dict["is_example"], _dict['user_id'], _dict["timer"], _dict["is_full"]]
    bool = mysql.sql_write(sql, args)
    # 拿到insert这一行的id
    if bool:
        sql = '''
            SELECT
                id
            FROM
                spider_setting 
            WHERE
                create_time =%s 
                AND group_name =%s 
                AND task_name =%s 
                AND first_url =%s 
                AND urls_xpath =%s 
                AND second_url =%s 
                AND is_example =%s 
                AND user_id =%s 
                AND timer =%s
                AND is_full =%s
        '''
        args = [create_time, _dict["group_name"], _dict['task_name'], _dict["first_url"],
                _dict["urls_xpath"], _dict["second_url"], _dict["is_example"], _dict['user_id'], _dict["timer"], _dict["is_full"]]
        id = mysql.sql_read(sql, args)[0]['id']
        create_table({'id': id})
        return id


def create_table(_dict={}):
    sql = '''
        CREATE TABLE `{}` (
          `id` bigint(20) NOT NULL AUTO_INCREMENT,
          `create_time` datetime NOT NULL,
          `second_url` varchar(500) NOT NULL,
          `first_url` varchar(500) NOT NULL,
          PRIMARY KEY (`id`),
          INDEX `ix-create_time` (`create_time`),
          INDEX `ix-second_url` (`second_url`)
        ) ENGINE=InnoDB;
        CREATE TABLE `{}` (
          `id` bigint(20) NOT NULL AUTO_INCREMENT,
          `url_id` bigint(20) NOT NULL,
          `create_time` datetime NOT NULL,
          `data` json NOT NULL,
          PRIMARY KEY (`id`),
          INDEX `ix-create_time` (`create_time`),
          INDEX `ix-url_id` (`url_id`)
        ) ENGINE=InnoDB;
    '''.format(SPIDER_URLS.format(_dict['id']), SPIDER_DATA.format(_dict['id']))
    bool = mysql.sql_write(sql)
    return bool
