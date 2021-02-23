from common.models import mysql


def delete_example(_dict={}):
    # 删除一条模板信息
    sql = 'DELETE FROM spider_setting WHERE id=%s'
    args = [_dict['id']]
    bool = mysql.sql_write(sql, args)
    return bool


def select_examples(_dict={}):
    sql = '''
        SELECT
            a.id,
            b.username,
            b.company,
            a.group_name,
            a.task_name,
            a.first_url,
            a.second_url,
            a.create_time,
            a.update_time
        FROM
            spider_setting AS a
            JOIN spider_user AS b ON b.id = a.user_id
        WHERE
            a.is_example = 1
    '''
    args = []
    if _dict:
        sql += ' AND a.user_id =%s'
        args.append(_dict['user_id'])
    examples = mysql.sql_read(sql=sql, args=args)
    return examples
