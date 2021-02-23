import re
import json
import socket
import itertools
from datetime import datetime
from urllib import parse

import asyncio
from aiohttp import web
import aiomysql
import aioredis

import config


async def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '', index)
    # spider_setting
    app.router.add_route('GET', '/spider_setting/select_setting', SpiderSetting.select_setting)
    app.router.add_route('GET', '/spider_setting/select_spiders', SpiderSetting.select_spiders)
    app.router.add_route('GET', '/spider_setting/update_progress', SpiderSetting.update_progress)
    app.router.add_route('GET', '/spider_setting/update_statistic', SpiderSetting.update_statistic)
    app.router.add_route('POST', '/spider_setting/update_setting', SpiderSetting.update_setting, expect_handler=web.Request.json)
    # spider_urls
    app.router.add_route('POST', '/spider_urls/select_urls', SpiderUrls.select_urls, expect_handler=web.Request.json)
    app.router.add_route('POST', '/spider_urls/insert_urls', SpiderUrls.insert_urls, expect_handler=web.Request.json)
    app.router.add_route('POST', '/spider_urls/delete_urls', SpiderUrls.delete_urls, expect_handler=web.Request.json)
    # spider_data
    app.router.add_route('GET', '/spider_data/select_urls', SpiderData.select_urls)
    app.router.add_route('POST', '/spider_data/insert_data', SpiderData.insert_data, expect_handler=web.Request.json)
    app.router.add_route('POST', '/spider_data/delete_data', SpiderData.delete_data, expect_handler=web.Request.json)
    # spider_logs
    app.router.add_route('GET', '/spider_logs/insert_html', SpiderLogs.insert_html)
    app.router.add_route('GET', '/spider_logs/select_html', SpiderLogs.select_html)
    app.router.add_route('GET', '/spider_logs/select_logs', SpiderLogs.select_logs)
    app.router.add_route('GET', '/spider_logs/insert_retry', SpiderLogs.insert_retry)
    app.router.add_route('GET', '/spider_logs/select_retry', SpiderLogs.select_retry)
    app.router.add_route('GET', '/spider_logs/remove_retry_one', SpiderLogs.remove_retry_one)
    app.router.add_route('GET', '/spider_logs/remove_retry_max', SpiderLogs.remove_retry_max)
    app.router.add_route('GET', '/spider_logs/delete_keys', SpiderLogs.delete_keys)

    server = await loop.create_server(app.make_handler(), '0.0.0.0', config.PORT)
    print('Server started at http://{}:{}'.format('127.0.0.1', config.PORT))
    return server


async def index(request):
    html = json.dumps({'service': 'sql', 'name': socket.gethostname(), 'addr': socket.gethostbyname(socket.gethostname())}) + '\n'
    return web.Response(text=html, content_type='text/plain', charset='utf-8')


MYSQL_CONN_POOL = None
REDIS_CONN_POOL = None


class ConnectionPool:
    @staticmethod
    async def mysql_conn_pool(loop):
        # 创建mysql链接池
        global MYSQL_CONN_POOL
        MYSQL_CONN_POOL = await aiomysql.create_pool(host=config.MYSQL_IP, port=int(config.MYSQL_PORT),
                                                     user=config.MYSQL_USER, password=config.MYSQL_PASSWORD,
                                                     db=config.MYSQL_DATABASE, charset='utf8', autocommit=True,
                                                     minsize=10, maxsize=100, loop=loop)

    @staticmethod
    async def redis_conn_pool(loop):
        # 创建redis链接池
        global REDIS_CONN_POOL
        address = 'redis://{}:{}'.format(config.REDIS_IP, config.REDIS_PORT)
        REDIS_CONN_POOL = await aioredis.create_redis_pool(address=address, encoding='utf8', minsize=10, maxsize=100,
                                                           loop=loop)

    @staticmethod
    async def sql_read(sql, args=None):
        # 读取数据库
        # print(re.sub(r'\s+', ' ', sql).strip())
        try:
            # sql = re.sub(r'%(?=[^s])', '%%', sql)
            with (await MYSQL_CONN_POOL) as conn:
                cursor = await conn.cursor()
                await cursor.execute(sql, args)
                columns = cursor.description
                data = await cursor.fetchall()
                # return data
                rows = []
                for row in data:
                    dictionary = {}
                    for key, value in zip(columns, row):
                        if isinstance(value, datetime):
                            dictionary[key[0]] = value.strftime('%Y-%m-%d %H:%M:%S')
                        else:
                            dictionary[key[0]] = str(value)
                    rows.append(dictionary)
                return rows
        except Exception as e:
            print('sql: {}\nerror: {}'.format(sql, e))
            return []

    @staticmethod
    async def sql_write(sql, args=None):
        # 写入数据库
        # print(re.sub(r'\s+', ' ', sql).strip())
        try:
            # sql = re.sub(r'%(?=[^s])', '%%', sql)
            with (await MYSQL_CONN_POOL) as conn:
                cursor = await conn.cursor()
                await cursor.execute(sql, args)
                return True
        except Exception as e:
            print('sql: {}\nerror: {}'.format(sql, e))
            return False


class SpiderSetting:
    '''
      `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'id',
      `create_time` datetime NOT NULL COMMENT '创建时间',
      `update_time` datetime NOT NULL DEFAULT '1970-01-01 08:00:00' COMMENT '更新时间',
      `group_name` varchar(50) NOT NULL COMMENT '分组名称',
      `task_name` varchar(50) NOT NULL COMMENT '任务名称',
      `is_example` int(11) NOT NULL DEFAULT '0' COMMENT '是否模板',
      `is_full` int(11) NOT NULL DEFAULT '0' COMMENT '是否全量',
      `first_urls` json DEFAULT NULL COMMENT '一级网址',
      `urls_xpath` varchar(200) NOT NULL DEFAULT '' COMMENT '网址xpath',
      `data_xpath` json DEFAULT NULL COMMENT '数据xpath',
      `first_url` varchar(200) NOT NULL DEFAULT '' COMMENT '测试一级网址',
      `second_url` varchar(200) NOT NULL DEFAULT '' COMMENT '测试二级网址',
      `timer` int(11) NOT NULL DEFAULT '0' COMMENT '定时采集',
      `urls_status` int(11) NOT NULL DEFAULT '0' COMMENT 'urls状态',
      `data_status` int(11) NOT NULL DEFAULT '0' COMMENT 'data状态',
      `begin_time` datetime NOT NULL DEFAULT '1970-01-01 08:00:00' COMMENT '开始时间',
      `finish_time` datetime NOT NULL DEFAULT '1970-01-01 08:00:00' COMMENT '结束时间',
      `progress` varchar(50) NOT NULL DEFAULT '0%=0/0(0)' COMMENT '采集进度',
      `user_id` bigint(20) NOT NULL COMMENT '用户id',
    '''

    @staticmethod
    async def select_setting(request):
        # 获取一条任务信息
        _args = dict(request.query)
        setting_id = _args['setting_id']
        sql = '''
            SELECT
                *
            FROM
                spider_setting 
            WHERE
                id ={}
        '''.format(setting_id)
        setting = await ConnectionPool.sql_read(sql)
        return web.Response(text=json.dumps(setting[0], ensure_ascii=False), content_type='text/plain', charset='utf-8')

    @staticmethod
    async def update_setting(request):
        # 更新一条任务信息
        _args = dict(await request.json())
        setting_id = _args['setting_id']
        updates = _args['updates']
        updates = ','.join(["`{}`='{}'".format(k, v) for k, v in updates.items()])
        sql = '''
            UPDATE
                spider_setting
            SET {}
            WHERE
                id ={}
        '''.format(updates, setting_id)
        bool = await ConnectionPool.sql_write(sql)
        return web.Response(text=str(bool), content_type='text/plain', charset='utf-8')

    @staticmethod
    async def update_progress(request):
        args = request.query
        setting_id = args['setting_id']
        progress = "CONCAT({},'%=',{},'/',{},'(',{},')')".format('CASE @c WHEN 0 THEN 0 ELSE ROUND(@a/@c*100,1) END',
                                                                 '@a', '@c', '@b')
        sql = '''
            SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
            SELECT @a:=COUNT(DISTINCT url_id),@b:=count(*) FROM {};
            SELECT @c:=count(*) FROM {};
            UPDATE spider_setting SET progress={} WHERE id={};
            SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ;
        '''.format(config.SPIDER_DATA.format(setting_id), config.SPIDER_URLS.format(setting_id), progress, setting_id)
        await ConnectionPool.sql_write(sql)
        return web.Response(text='True', content_type='text/plain', charset='utf-8')

    @staticmethod
    async def select_spiders(request):
        # 查找需要采集的任务
        _args = dict(request.query)
        type = _args['type'].upper()
        if type == 'URLS':
            sql = "SELECT id FROM spider_setting WHERE urls_status+data_status >= 1"
        elif type == 'DATA':
            sql = "SELECT id FROM spider_setting WHERE data_status=1"
        elif type == 'TIMER':
            sql = "SELECT id,urls_status,data_status,begin_time,finish_time,timer FROM spider_setting WHERE timer>=1"
        elif type == 'ALL':
            sql = "SELECT id,urls_status,data_status,begin_time,finish_time,timer FROM spider_setting WHERE urls_status+data_status+timer>0"
        else:
            sql = ''
        spiders = sql and await ConnectionPool.sql_read(sql=sql) or []
        return web.Response(text=json.dumps(spiders, ensure_ascii=False), content_type='text/plain', charset='utf-8')

    @staticmethod
    async def update_statistic(request):
        # 统计每天抓取数量和总得抓取条数
        sql1 = """
            INSERT INTO spider_count_temp ( table_name, table_rows )
            SELECT TABLE_NAME, 0 FROM information_schema.`TABLES` a 
            WHERE a.TABLE_SCHEMA = '{}' AND a.TABLE_NAME LIKE 'spider_data_%' AND NOT EXISTS ( SELECT * FROM spider_count_temp b WHERE a.TABLE_NAME = b.table_name );
        """.format(config.MYSQL_DATABASE)
        sql2 = """
            UPDATE spider_count_temp a
            JOIN information_schema.`TABLES` b ON b.TABLE_SCHEMA = '{}' AND b.TABLE_NAME LIKE 'spider_data_%' AND a.table_name = b.TABLE_NAME
            SET a.table_rows = b.TABLE_ROWS;
        """.format(config.MYSQL_DATABASE)
        sql3 = """
            INSERT INTO spider_count ( count_time, table_count, row_count )
            SELECT CURRENT_DATE, count( table_name ), sum( table_rows ) + 26446556 FROM spider_count_temp;
        """
        await ConnectionPool.sql_write(sql1)
        await ConnectionPool.sql_write(sql2)
        await ConnectionPool.sql_write(sql3)
        return web.Response(text='success', content_type='text/plain', charset='utf-8')


class SpiderUrls:
    @staticmethod
    async def select_urls(request):
        _args = await request.json()
        setting = json.loads(_args['setting'])
        sql = '''
            SELECT DISTINCT
                first_url 
            FROM
                {} 
            WHERE
                create_time > ( SELECT finish_time FROM spider_setting WHERE id ={} )
        '''.format(config.SPIDER_URLS.format(setting['id']), setting['id'])
        finished_first_urls = await ConnectionPool.sql_read(sql)
        generate_first_urls = SpiderUrls._generate_first_urls(setting['first_urls'])
        for first_url in finished_first_urls:
            try:
                generate_first_urls.remove(first_url['first_url'])
            except:
                pass
        return web.Response(text=json.dumps(generate_first_urls, ensure_ascii=False), content_type='text/plain',
                            charset='utf-8')

    @staticmethod
    async def insert_urls(request):
        # 存入网址
        _args = await request.json()
        setting = _args['setting']
        first_url = _args['first_url']
        second_urls = _args['second_urls']
        in_clause = "'{}'".format("','".join(second_urls))
        sql = "SELECT second_url FROM {} WHERE second_url IN ({})".format(config.SPIDER_URLS.format(setting['id']),
                                                                          in_clause)
        # 全量采集
        sql = setting['is_full'] == '1' and "{} AND create_time>'{}';".format(sql,
                                                                              setting['finish_time']) or "{};".format(
            sql)
        existing_second_urls = await ConnectionPool.sql_read(sql)
        for row in existing_second_urls:
            if row['second_url'] in second_urls:
                second_urls.remove(row['second_url'])
        if second_urls:
            sql = 'INSERT INTO {}(create_time,second_url,first_url) VALUES'.format(
                config.SPIDER_URLS.format(setting['id']))
            for second_url in second_urls:
                sql = sql + "('{}','{}','{}'),".format(datetime.now(), second_url, first_url)
            sql = sql[0:-1]  # 去除末尾逗号
            await ConnectionPool.sql_write(sql)
            await SpiderLogs.insert_logs(setting['id'], first_url, second_urls, 'URLS')
        return web.Response(text='success', content_type='text/plain', charset='utf-8')

    @staticmethod
    async def delete_urls(request):
        args = await request.json()
        setting_id = args['setting_id']
        del_ids = args['del_ids']
        sql = 'DELETE FROM {} WHERE id IN ({});'.format(config.SPIDER_URLS.format(setting_id), ','.join(del_ids))
        await ConnectionPool.sql_write(sql)
        return web.Response(text='success', content_type='text/plain', charset='utf-8')

    @staticmethod
    def _generate_first_urls(_first_urls):
        urls = []
        first_urls_list = json.loads(_first_urls)
        for first_urls in first_urls_list:
            items = re.findall('{.*?}', first_urls)
            if items:
                args = []
                for item in items:
                    if re.findall('-', item):
                        interval = re.findall(r'\d+', item)
                        args.append([i for i in range(int(interval[0]), int(interval[1]) + 1)])
                    else:
                        args.append(item[1:-1].split(','))
                for i in itertools.product(*args):
                    urls.append(re.sub('{.*?}', '{}', first_urls).format(*i))
            else:
                urls.append(first_urls)
        return urls


class SpiderData:
    @staticmethod
    async def select_urls(request):
        # 得到limit个未采集的二级网址的
        _args = dict(request.query)
        setting_id = _args['setting_id']
        limit = int(_args['limit'])
        sql = '''
            SELECT
                id,
                second_url 
            FROM
                {} a 
            WHERE
                NOT EXISTS ( SELECT 1 FROM {} b WHERE a.id = b.url_id ) 
                LIMIT {};
        '''.format(config.SPIDER_URLS.format(setting_id), config.SPIDER_DATA.format(setting_id), limit)
        second_urls = await ConnectionPool.sql_read(sql)
        return web.Response(text=json.dumps(second_urls, ensure_ascii=False), content_type='text/plain',
                            charset='utf-8')

    @staticmethod
    async def insert_data(request):
        # 存入数据
        args = await request.json()
        setting_id = args['setting_id']
        id = args['id']
        second_url = args['second_url']
        data = args['data']
        if data:
            sql = 'INSERT INTO {}(url_id,create_time,`data`) VALUES'.format(config.SPIDER_DATA.format(setting_id))
            for item in data:
                sql = sql + "('{}','{}','{}'),".format(id, datetime.now(), json.dumps(item, ensure_ascii=False).replace('\\\\', '\\'))
            # 去除末尾逗号
            sql = sql[0:-1]
            await ConnectionPool.sql_write(sql)
            await SpiderLogs.insert_logs(setting_id, second_url, data, 'DATA')
        return web.Response(text='success', content_type='text/plain', charset='utf-8')

    @staticmethod
    async def delete_data(request):
        # 校正数据，删除超过重试次数、但已采集的数据
        args = await request.json()
        setting_id = args['setting_id']
        sql = 'DELETE a FROM {} a WHERE NOT EXISTS (SELECT * FROM {} b WHERE a.url_id=b.id);'.format(config.SPIDER_DATA.format(setting_id), config.SPIDER_URLS.format(setting_id))
        await ConnectionPool.sql_write(sql)
        return web.Response(text='success', content_type='text/plain', charset='utf-8')


class SpiderLogs:
    retry_one = 'RETRY_ONE_{}'
    retry_max = 'RETRY_MAX_{}'
    urls = 'URLS_{}'
    data = 'DATA_{}'

    @staticmethod
    async def insert_html(request):
        args = await request.json()
        url = parse.unquote(args['url'])
        html = args['html']
        with await REDIS_CONN_POOL as conn:
            await conn.set(url, html, ex=60 * 60)
        return web.Response(text='success', content_type='text/plain', charset='utf-8')

    @staticmethod
    async def select_html(request):
        args = dict(request.query)
        url = parse.unquote(args['url'])
        with await REDIS_CONN_POOL as conn:
            html = await conn.get(url)
        return web.Response(text=html, content_type='text/plain', charset='utf-8')

    # Redis存储
    @staticmethod
    async def insert_logs(id, url, data, type):
        # 插入采集日志
        key = "{}_{}".format(type.upper(), id)
        value = 'create_time: {}, url: {}, data: {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), url, data)
        with await REDIS_CONN_POOL as conn:
            await conn.lpush(key, value)
            await conn.ltrim(key, 0, config.MAX_LOGS - 1)

    @staticmethod
    async def select_logs(request):
        # 读取采集日志
        args = dict(request.query)
        key = "{}_{}".format(args["type"].upper(), args['id'])
        with await REDIS_CONN_POOL as conn:
            logs = await conn.lrange(key, 0, config.MAX_LOGS - 1)
        return web.Response(text=json.dumps(logs, ensure_ascii=False), content_type='application/json', charset='utf-8',
                            headers={"Access-Control-Allow-Origin": "*"})

    @staticmethod
    async def insert_retry(request):
        # 默认添加至RETRY_ONE，如果已存在，则移动至RETRY_MAX
        args = dict(request.query)
        key = args['key']
        value = args['value']
        lua_script = '''
            if (redis.call("SADD",KEYS[1],ARGV[1])==0) then
                redis.call("SMOVE",KEYS[1],KEYS[2],ARGV[1])
            end
        '''
        with await REDIS_CONN_POOL as conn:
            result = await conn.eval(lua_script, [SpiderLogs.retry_one.format(key), SpiderLogs.retry_max.format(key)],
                                     [value])
        return web.Response(text=str(result), content_type='application/json', charset='utf-8')

    @staticmethod
    async def select_retry(request):
        # 返回RETRY_MAX，即达到最大超时次数的id列表
        args = dict(request.query)
        key = args['key']
        with await REDIS_CONN_POOL as conn:
            value = await conn.smembers(SpiderLogs.retry_max.format(key))
        return web.Response(text=json.dumps(value), content_type='application/json', charset='utf-8')

    @staticmethod
    async def remove_retry_one(request):
        # 从RETRY_ONE中弹出，一次一个
        args = dict(request.query)
        key = args['key']
        value = args['value']
        with await REDIS_CONN_POOL as conn:
            result = await conn.srem(SpiderLogs.retry_one.format(key), int(value))
        return web.Response(text=str(result), content_type='application/json', charset='utf-8')

    @staticmethod
    async def remove_retry_max(request):
        # 从RETRY_MAX中弹出，一次多个
        args = dict(request.query)
        key = args['key']
        value = json.loads(args['value'])
        with await REDIS_CONN_POOL as conn:
            result = await conn.srem(SpiderLogs.retry_max.format(key), *[int(item) for item in value])
        return web.Response(text=str(result), content_type='application/json', charset='utf-8')

    @staticmethod
    async def delete_keys(request):
        # 任务结束，删除所有
        args = dict(request.query)
        setting_id = json.loads(args['setting_id'])
        with await REDIS_CONN_POOL as conn:
            result = await conn.delete(SpiderLogs.retry_one.format(setting_id), SpiderLogs.retry_max.format(setting_id),
                                       SpiderLogs.urls.format(setting_id), SpiderLogs.data.format(setting_id))
        return web.Response(text=str(result), content_type='application/json', charset='utf-8')


async def main(loop):
    task = [init(loop), ConnectionPool.mysql_conn_pool(loop), ConnectionPool.redis_conn_pool(loop)]
    await asyncio.gather(*task)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.run_forever()
