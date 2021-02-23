import config
import json
import time
from collections import OrderedDict
import socket
from copy import deepcopy

from aiohttp import web, ClientSession
import asyncio


async def get_html(url):
    try:
        async with ClientSession() as session:
            async with session.get(url=url, timeout=config.TIMEOUT) as resp:
                html = await resp.text()
            return html
    except Exception as e:
        return ''


RAW_POOL = OrderedDict()
PROXY_POOL = set()


async def get_proxy():
    # 通过API获取代理IP
    while True:
        try:
            now = time.time()
            html = json.loads(await get_html(config.API))

            global RAW_POOL, PROXY_POOL
            keys = deepcopy(list(RAW_POOL.keys()))
            for key in keys:
                if now - key > config.API_EXPIRE:
                    PROXY_POOL = PROXY_POOL - RAW_POOL[key]
                    RAW_POOL.pop(key)
                else:
                    break

            # add_proxy
            if html['code'] == '0':
                ips = ['http://{}:{}'.format(item['ip'], item['port']) for item in html['msg']]
                PROXY_POOL.update(ips)
            else:
                ips = [html['msg']]
            RAW_POOL[now] = set(ips)
        except Exception as e:
            print(e)
        finally:
            await asyncio.sleep(config.API_FREQUENCY)


async def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '', index)
    app.router.add_route('GET', '/pool', pool)
    await loop.create_server(app.make_handler(), '0.0.0.0', config.PORT)
    print('Server started at http://{}:{}'.format('127.0.0.1', config.PORT))
    await get_proxy()


async def index(request):
    html = json.dumps({'service': 'proxy', 'name': socket.gethostname(), 'addr': socket.gethostbyname(socket.gethostname())}) + '\n'
    keys = sorted(RAW_POOL.keys(), reverse=True)[:15]
    for key in keys:
        html = html + '{}({})\n{}\n'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(key)), key, RAW_POOL[key])
    return web.Response(text=html, content_type='text/text', charset='utf-8')


async def pool(request):
    proxy = json.dumps(list(PROXY_POOL))
    return web.Response(text=proxy, content_type='text/text', charset='utf-8')


if __name__ == '__main__':
    # 主线程
    main_loop = asyncio.get_event_loop()
    main_loop.run_until_complete(init(main_loop))
    main_loop.run_forever()
