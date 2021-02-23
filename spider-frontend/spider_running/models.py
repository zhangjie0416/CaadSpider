import json

from common.models import mysql
from spider.settings import SPIDER_URLS, SPIDER_DATA


def select_details(_dict={}):
    sql = '''
                SELECT
                    data_xpath
                FROM
                    spider_setting
                WHERE
                    id =%s
            '''
    args = [_dict['id']]
    detail = mysql.sql_read(sql, args)
    detail = detail[0]["data_xpath"]
    # 固定采集
    fix_fields = json.loads(detail)['fix_fields']
    fix_fields = sorted(fix_fields, key=lambda field: field['seq'])
    fix_fields = [item['field'] for item in fix_fields]
    # 单台采集
    one_fields = json.loads(detail)['one_fields']
    one_fields = sorted(one_fields, key=lambda field: field['seq'])
    one_fields = [item['field'] for item in one_fields]
    # 多条采集
    all_fields = json.loads(detail)['all_fields']
    all_fields = sorted(all_fields, key=lambda field: field['seq'])
    all_fields = [item['field'] for item in all_fields]

    fields = fix_fields + one_fields + all_fields
    return fields


def update_running(_dict={}):
    # 更新任务信息
    sql = 'UPDATE spider_setting SET data_status=%s,urls_status=%s WHERE id IN ({});'.format(_dict['id'])
    args = [_dict['status'], _dict['status']]
    bool = mysql.sql_write(sql, args)
    return bool


def delete_running(_dict={}):
    # 删除一个任务
    sql = 'DELETE FROM spider_setting WHERE id={};DROP TABLE IF EXISTS {};DROP TABLE IF EXISTS {};'.format(_dict['id'], SPIDER_URLS.format(_dict['id']), SPIDER_DATA.format(_dict['id']))
    bool = mysql.sql_write(sql=sql)
    return bool


def select_runnings(_dict={}):
    sql = '''
        SELECT
            a.id,
            b.username,
            b.company,
            a.create_time,
            a.update_time,
            a.group_name,
            a.task_name,
            a.timer,
            CASE WHEN a.data_status + a.urls_status > 0 THEN 1 ELSE 0 END AS 'data_status',
            a.progress,
            a.begin_time,
            a.finish_time,
            a.is_full
        FROM
            spider_setting AS a
            JOIN spider_user AS b ON b.id = a.user_id
        WHERE
            (a.create_time >= %s OR a.finish_time >= %s)
            AND a.is_example = 0
            AND (CASE WHEN a.data_status + a.urls_status > 0 THEN 1 ELSE 0 END) =%s
    '''
    args = [_dict['from_date'], _dict['from_date'], _dict['data_status']]
    if _dict['username'] != 'spider':
        sql += ' AND a.user_id =%s'
        args.append(_dict['user_id'])
    runnings = mysql.sql_read(sql, args)
    return runnings


def update_setting_timer(_dict):
    sql = '''
        UPDATE spider_setting 
        SET timer = %s 
        WHERE
            id IN ({})
    '''.format(_dict['id'])
    args = [_dict['timer']]
    bool = mysql.sql_write(sql, args)
    return bool
