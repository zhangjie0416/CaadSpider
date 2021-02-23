import datetime
import re

from django.db import connections


def sql_read(sql='', args=[], id=0):
    try:
        # 分表spider_data_1:{table_name}_{task_id}
        sql = re.sub(r'%(?=[^s])', '%%', sql)
        cursor = connections['default'].cursor()
        cursor.execute(sql, args)
        columns = [column[0] for column in cursor.description]
        rows = []
        for row in cursor.fetchall():
            dictionary = {}
            for key, value in zip(columns, row):
                if value is None:
                    dictionary[key] = ''
                elif isinstance(value, datetime.datetime):
                    dictionary[key] = value.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(value, bytes):
                    dictionary[key] = value.decode('utf-8')
                else:
                    dictionary[key] = str(value)
            rows.append(dictionary)
        return rows
    except Exception as e:
        print(e)
        return []


def sql_read_raw(sql='', args=[]):
    try:
        # 分表spider_data_1:{table_name}_{task_id}
        sql = re.sub(r'%(?=[^s])', '%%', sql)
        cursor = connections['default'].cursor()
        cursor.execute(sql, args)
        columns = [column[0] for column in cursor.description]
        rows = [columns]
        for _row in cursor.fetchall():
            row = []
            for value in _row:
                if value is None:
                    value = ''
                elif isinstance(value, datetime.datetime):
                    value = value.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(value, bytes):
                    value = value.decode('utf-8')
                else:
                    value = str(value)
                row.append(value)
            rows.append(row)
        return rows
    except Exception as e:
        print(e)
        return []


def sql_write(sql='', args=[]):
    try:
        # 分表spider_data_1:{table_name}_{task_id}
        # sql = re.sub(r'%(?=[^s])', '%%', sql)
        cursor = connections['default'].cursor()
        cursor.execute(sql, args)
        return True
    except Exception as e:
        print(e)
        return False
