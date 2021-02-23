from common.models import mysql
from spider_running.models import select_details
from common.models import write2file
from spider.settings import DATABASES, EXCEL_PATH, SPIDER_URLS, SPIDER_DATA
import os
import zipfile


def select_setting(_dict={}):
    sql = '''
        SELECT
            a.group_name,
            a.task_name 
        FROM
            spider_setting a
            JOIN spider_user b ON b.id = a.user_id 
        WHERE
            a.id =%s
    '''
    args = [_dict['id']]
    if _dict['username'] != 'spider':
        sql += ' AND b.username =%s'
        args.append(_dict['username'])
    setting = mysql.sql_read(sql=sql, args=args)
    return setting


def select_columns(_dict):
    fields = select_details(_dict)
    columns = ''
    for field in fields:
        columns = '''{}JSON_UNQUOTE ( data -> '$."{}"' ) AS '{}','''.format(columns, field, field)
    if columns:
        columns = columns[0:-1]  # 去除尾部多余的逗号
    return columns


def to_html(_dict={}):
    try:
        # 1.用户验证
        setting = select_setting(_dict)
        if not setting: return []

        # 2.获取字段
        columns = select_columns(_dict)
        if not columns: return []

        # 3.获取数据
        sql = '''
                SELECT
                    a.create_time AS '采集时间',
                    b.second_url AS '采集网址',
                    {}
                FROM
                    {} a JOIN {} b ON a.url_id = b.id 
                WHERE
                    a.create_time >= '{}'
                    AND a.create_time <= '{}'
                ORDER BY a.create_time DESC
                LIMIT 200
            '''.format(columns, SPIDER_DATA.format(_dict['id']), SPIDER_URLS.format(_dict['id']), _dict['begin_date'], _dict['end_date'])
        data = mysql.sql_read(sql)
    except:
        data = []
    return data


def to_excel(_dict):
    try:
        # 1.用户验证
        setting = select_setting(_dict)
        if not setting: return []

        # 2.获取字段
        columns = select_columns(_dict)
        if not columns: return []

        sql = '''
                SELECT
                    a.create_time AS '采集时间',
                    b.second_url AS '采集网址',
                    {}
                FROM
                    {} a JOIN {} b ON a.url_id = b.id 
                WHERE
                    a.create_time >= '{}'
                    AND a.create_time <= '{}'
            '''.format(columns, SPIDER_DATA.format(_dict['id']), SPIDER_URLS.format(_dict['id']), _dict['begin_date'], _dict['end_date'])
        data = mysql.sql_read_raw(sql)
        if not os.path.exists(EXCEL_PATH):
            os.makedirs(EXCEL_PATH)
        filename = '{}-{}_{}-{}'.format(setting[0]['group_name'], setting[0]['task_name'], _dict['begin_date'][0:10].replace('-', ''), _dict['end_date'][0:10].replace('-', ''))
        if len(data) > 10000:
            filename += '.csv'
            write2file.to_csv(data, EXCEL_PATH + filename)
        else:
            filename += '.xlsx'
            write2file.to_excel(data, EXCEL_PATH + filename)
    except Exception as e:
        print(e)
        filename = ''
    finally:
        return filename


def zip_excels(file_list, zip_name):
    with zipfile.ZipFile(EXCEL_PATH + zip_name, mode='w') as zipf:
        for file in file_list:
            zipf.write(EXCEL_PATH + file)
            os.remove(EXCEL_PATH + file)
