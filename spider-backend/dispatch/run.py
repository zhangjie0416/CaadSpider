import json
from json import JSONDecodeError
from datetime import datetime
import time
import socket

from aiohttp import web, ClientSession
import asyncio

import config

URLS_IDs_POOL = set()
DATA_IDs_POOL = set()


class SpiderCommon:
    @staticmethod
    async def get_html(url, json=None):
        try:
            async with ClientSession() as session:
                if json:
                    async with session.post(url=url, json=json, timeout=8) as resp:
                        html = await resp.text()
                else:
                    async with session.get(url=url) as resp:
                        html = await resp.text()
                return html
        except Exception as e:
            print(e)
            return ''

    @staticmethod
    async def log2disk(content):
        print(content)


async def index(request):
    html = json.dumps({'service': 'dispatch', 'name': socket.gethostname(), 'addr': socket.gethostbyname(socket.gethostname())}) + '\n'
    html = '{}\nurls:{}\ndata:{}\n'.format(html, URLS_IDs_POOL or '{}', DATA_IDs_POOL or '{}')
    return web.Response(text=html, content_type='text/text', charset='utf-8')


class SpiderMonitor:
    @staticmethod
    async def spider_monitor(loop):
        app = web.Application(loop=loop)
        app.router.add_route('GET', '', index)
        await loop.create_server(app.make_handler(), '0.0.0.0', config.PORT)
        print('Server started at http://{}:{}'.format('127.0.0.1', config.PORT))
        # proxy先运行60秒
        await asyncio.sleep(60)
        while True:
            try:
                rows = json.loads(await SpiderCommon.get_html(config.SpiderSetting_select_spiders.format('all')))
                rows_urls = set(row['id'] for row in rows if row['urls_status'] == '1')
                rows_data = set(row['id'] for row in rows if row['data_status'] == '1')
                rows_timer = [row for row in rows if int(row['timer']) > 0]
                print(datetime.now(), 'urls:', rows_urls or '{}', 'data:', rows_data or '{}')
                await SpiderMonitor.start_urls(loop, rows_urls)
                await SpiderMonitor.start_data(loop, rows_data)
                await SpiderMonitor.start_timer(loop, rows_timer)
            except JSONDecodeError:
                print('error: 请检查{}'.format(config.SpiderSetting_select_spiders.format('all')))
            finally:
                await asyncio.sleep(10)

    @staticmethod
    async def start_urls(loop, rows):
        urls_ids = rows - URLS_IDs_POOL  # 防止重复运行
        for setting_id in urls_ids:
            asyncio.run_coroutine_threadsafe(SpiderRun.start_urls(setting_id), loop)
            URLS_IDs_POOL.add(setting_id)

    @staticmethod
    async def start_data(loop, rows):
        data_ids = rows - DATA_IDs_POOL  # 防止重复运行
        for setting_id in data_ids:
            asyncio.run_coroutine_threadsafe(SpiderRun.start_data(setting_id), loop)
            DATA_IDs_POOL.add(setting_id)

    @staticmethod
    async def start_timer(loop, rows):
        if time.localtime()[3] == 0 and time.localtime()[4] == 0 and time.localtime()[5] >= 0 and time.localtime()[5] < 10:
            await SpiderCommon.get_html(url=config.SpiderSetting_update_statistic)
        for row in rows:
            if row["finish_time"] == "1970-01-01 08:00:00" and row['urls_status'] == '0' and row['data_status'] == '0':  # 新创建任务
                continue
            begin_time = time.mktime(time.strptime(row["begin_time"], "%Y-%m-%d %H:%M:%S"))
            timer = int(row['timer'])
            restart_time = begin_time + (60 * 60 * 24 * timer)
            if restart_time <= time.time():
                if row['urls_status'] == '1' or row['data_status'] == '1':
                    # 如果当前任务未停止：
                    await SpiderCommon.get_html(url=config.SpiderSetting_update_setting,
                                                json={'setting_id': row['id'],
                                                      'updates': {'urls_status': '0', 'data_status': '0', 'finish_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}})  # 更新为结束状态
                    try:
                        URLS_IDs_POOL.remove(row['id'])
                        DATA_IDs_POOL.remove(row['id'])
                    except KeyError:
                        pass
                # 重启任务
                await SpiderCommon.get_html(url=config.SpiderSetting_update_setting,
                                            json={'setting_id': row['id'],
                                                  'updates': {'urls_status': '1', 'data_status': '1', 'begin_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}})  # 更新为开始状态


class SpiderRun:
    @staticmethod
    async def start_urls(setting_id):
        log = "{}||采集网址开始：setting_id={}".format(datetime.now(), setting_id)
        await SpiderCommon.log2disk(log)
        setting = await SpiderCommon.get_html(config.SpiderSetting_select_setting.format(setting_id))
        first_urls = json.loads(await SpiderCommon.get_html(url=config.SpiderUrls_select_urls, json={'setting': setting}))  # 得到一级网址
        pages = len(first_urls) % config.URLS_CONCURRENCE > 0 and len(first_urls) // config.URLS_CONCURRENCE + 1 or len(first_urls) // config.URLS_CONCURRENCE
        '''
        开始
        '''
        # 根据URLS_CONCURRENCE分片
        for i in range(pages):
            setting = await SpiderCommon.get_html(config.SpiderSetting_select_setting.format(setting_id))  # 循环前获取setting['urls_status']，用于判断采集网址是否手动暂停
            setting = json.loads(setting)
            if setting['urls_status'] == '0':  # 任务手动结束
                log = "{}||采集网址暂停：setting_id={}".format(datetime.now(), setting_id)
                await SpiderCommon.log2disk(log)
                break
            urls = first_urls[i * config.URLS_CONCURRENCE: (i + 1) * config.URLS_CONCURRENCE]  # 获取分片网址
            print('setting_id:', setting_id, ', urls:', config.URLS_CONCURRENCE)
            await SpiderCommon.get_html(url=config.Store_spider_urls, json={'setting': setting, 'urls': urls})
            await asyncio.sleep(10)
            await SpiderCommon.get_html(url=config.SpiderSetting_update_progress.format(setting_id))
        '''
        结束
        '''
        await SpiderCommon.get_html(url=config.SpiderSetting_update_setting, json={'setting_id': setting_id, 'updates': {'urls_status': '0'}})  # 更新urls状态
        URLS_IDs_POOL.remove(setting_id)  # 任务结束删除id，防止无法重新开始
        log = "{}||采集网址结束：setting_id={}".format(datetime.now(), setting_id)
        await SpiderCommon.log2disk(log)

    @staticmethod
    async def start_data(setting_id):
        log = "{}||采集内容开始：setting_id={}".format(datetime.now(), setting_id)
        await SpiderCommon.log2disk(log)
        await SpiderCommon.get_html(url=config.SpiderSetting_update_setting,
                                    json={'setting_id': setting_id, 'updates': {'begin_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}})  # 更新data状态
        is_pause = False  # 是否手动暂停
        '''
        开始
        '''
        while True:
            setting = await SpiderCommon.get_html(config.SpiderSetting_select_setting.format(setting_id))  # 循环前获取setting['data_status']，用于判断采集数据是否手动暂停
            setting = json.loads(setting)
            if setting['data_status'] == '0':  # 任务手动结束
                is_pause = True
                log = "{}||采集内容暂停：setting_id={}".format(datetime.now(), setting_id)
                await SpiderCommon.log2disk(log)
                break
            second_urls = json.loads(await SpiderCommon.get_html(config.SpiderData_select_urls.format(setting_id, config.DATA_CONCURRENCE)))  # 获取limit条二级网址
            print('setting_id:', setting_id, ', second_urls:', config.DATA_CONCURRENCE)
            if second_urls:  # 是否还有未采集的
                await SpiderCommon.get_html(url=config.Store_spider_data, json={'setting': setting, 'urls': second_urls})
                await SpiderCommon.get_html(url=config.SpiderSetting_update_progress.format(setting_id))
            else:
                if setting['urls_status'] == '0':  # 自动采集完成
                    break
                log = "setting_id={}:采集网址未结束，等待新的二级网址".format(setting_id)  # 未结束等待10秒
                await SpiderCommon.log2disk(log)
            await asyncio.sleep(10)
        '''
        结束
        '''
        await SpiderCommon.get_html(url=config.SpiderData_delete_data, json={'setting_id': setting_id})  # 校正最终进度
        await SpiderCommon.get_html(url=config.SpiderSetting_update_progress.format(setting_id))  # 校正最终进度
        if is_pause:
            await SpiderCommon.get_html(url=config.SpiderSetting_update_setting, json={'setting_id': setting_id, 'updates': {'data_status': '0'}})  # 更新data状态
        else:
            await SpiderCommon.get_html(url=config.SpiderSetting_update_setting,
                                        json={'setting_id': setting_id,
                                              'updates': {'data_status': '0', 'finish_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}})  # 更新data状态，任务结束时间
        DATA_IDs_POOL.remove(setting_id)  # 任务结束删除id，防止无法重新开始
        log = "{}||采集内容结束：setting_id={}".format(datetime.now(), setting_id)
        await SpiderCommon.log2disk(log)
        await SpiderCommon.get_html(url=config.DELETE_KEYS.format(setting_id=setting['id']))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    future = SpiderMonitor.spider_monitor(loop)
    loop.run_until_complete(future)
    loop.run_forever()
