import json
import asyncio
from datetime import datetime
import config
from aiohttp import web, ClientSession
from urllib import parse
from threading import Thread
import socket


async def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '', index)
    app.router.add_route('POST', '/crawl_urls', SpiderUrls.spider_urls, expect_handler=web.Request.json)
    app.router.add_route('POST', '/crawl_data', SpiderData.spider_data, expect_handler=web.Request.json)
    server = await loop.create_server(app.make_handler(), '0.0.0.0', config.PORT)
    print('Server started at http://{}:{}'.format('127.0.0.1', config.PORT))
    return server


async def index(request):
    html = json.dumps({'service': 'store', 'name': socket.gethostname(), 'addr': socket.gethostbyname(socket.gethostname())}) + '\n'
    return web.Response(text=html, content_type='text/text', charset='utf-8')


class SpiderCommon:
    @staticmethod
    async def get_html(url, _json=None):
        try:
            async with ClientSession() as session:
                if _json:
                    async with session.post(url=url, json=_json, timeout=8) as resp:
                        html = await resp.text()
                else:
                    async with session.get(url=url) as resp:
                        html = await resp.text()
                return html
        except Exception as e:
            return ''

    @staticmethod
    async def log2disk(content):
        print(content)


class SpiderUrls:
    @staticmethod
    async def spider_urls(request):
        args = await request.json()
        setting = args['setting']
        urls = args['urls']
        asyncio.run_coroutine_threadsafe(SpiderUrls.spider_future(setting, urls), crawl_urls_loop)
        return web.Response(text="success", content_type='text/text', charset='utf-8')

    @staticmethod
    async def spider_future(setting, urls):
        tasks = [SpiderUrls._spider_urls(setting, url) for url in urls]
        await asyncio.gather(*tasks)

    @staticmethod
    def spider_loop(loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    @staticmethod
    async def _spider_urls(setting, url):
        # 提取详情页的url
        if setting['urls_xpath']:
            post_data = {'url': url, 'xpath': setting['urls_xpath']}
            second_urls = await SpiderCommon.get_html(url=config.PARSE_API, _json=post_data)
        else:
            second_urls = '["{}"]'.format(url)
        second_urls = json.loads(second_urls)
        num = len(second_urls)
        if num:
            post_data = {'setting': setting, 'first_url': url, 'second_urls': second_urls}
            await SpiderCommon.get_html(url=config.INSERT_URLS, _json=post_data)  # 将second_url 存入数据库
            log = "{}||setting_id: {}||一级网址：{}||二级网址：{}".format(datetime.now(), setting['id'], url, num)
            await SpiderCommon.log2disk(log)


class SpiderData:
    @staticmethod
    async def spider_data(request):
        args = await request.json()
        setting = args['setting']
        urls = args['urls']
        asyncio.run_coroutine_threadsafe(SpiderData.spider_future(setting, urls), crawl_urls_loop)
        return web.Response(text="success", content_type='text/text', charset='utf-8')

    @staticmethod
    async def spider_future(setting, urls):
        tasks = [SpiderData._spider_data(setting, url['second_url'], url['id']) for url in urls] + [SpiderData.delete_urls(setting)]
        await asyncio.gather(*tasks)

    @staticmethod
    def spider_loop(loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    @staticmethod
    async def _spider_data(setting, url, id):
        data = await SpiderCommon.get_html(url=config.PARSE_API, _json={'url': parse.quote(url), 'xpath': setting['data_xpath']})
        data = json.loads(data)  # list
        if data:
            await SpiderCommon.get_html(url=config.INSERT_DATA, _json={'setting_id': setting['id'], 'id': id, 'second_url': url, 'data': data})
            log = "{}||setting_id: {}||二级网址：{}||采集字段：{}".format(datetime.now(), setting['id'], url, len(data))
            await SpiderCommon.log2disk(log)
            await SpiderCommon.get_html(url=config.REMOVE_RETRY_ONE.format(key=setting['id'], value=id))
        else:
            await SpiderCommon.get_html(url=config.INSERT_RETRY.format(key=setting['id'], value=id))

    @staticmethod
    async def delete_urls(setting):
        del_ids = await SpiderCommon.get_html(url=config.SELECT_RETRY.format(key=setting['id']))
        del_ids_json = json.loads(del_ids)
        if del_ids_json:
            await SpiderCommon.get_html(url=config.DELETE_URLS, _json={'del_ids': del_ids_json, 'setting_id': setting['id']})
            await SpiderCommon.get_html(url=config.REMOVE_RETRY_MAX.format(key=setting['id'], value=del_ids))
            print('DELETED: RETRY_MAX_{}'.format(setting['id']), del_ids)


if __name__ == '__main__':
    # urls协程
    crawl_urls_loop = asyncio.new_event_loop()
    crawl_urls_thread = Thread(target=SpiderUrls.spider_loop, args=(crawl_urls_loop,))
    crawl_urls_thread.start()
    # data协程
    crawl_data_loop = asyncio.new_event_loop()
    crawl_data_thread = Thread(target=SpiderData.spider_loop, args=(crawl_data_loop,))
    crawl_data_thread.start()
    # web协程
    loop = asyncio.new_event_loop()
    loop.run_until_complete(init(loop))
    loop.run_forever()
