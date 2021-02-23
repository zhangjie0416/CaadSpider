import re
import random
import config
import asyncio
from urllib import parse
from threading import Thread
from aiohttp import web, ClientSession
import socket
import json
from datetime import datetime

PROXY_POOL = []


async def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '', index)
    app.router.add_route('GET', '/download', download)
    server = await loop.create_server(app.make_handler(), '0.0.0.0', config.PORT)
    print('Server started at http://{}:{}'.format('127.0.0.1', config.PORT))
    return server


async def index(request):
    html = json.dumps({'service': 'download', 'name': socket.gethostname(), 'addr': socket.gethostbyname(socket.gethostname())}) + '\n'
    for i, proxy in enumerate(PROXY_POOL):
        html = html + (PROXY_POOL[i] + ',').ljust(30)
        if (i + 1) % 8 == 0:
            html += '\n'
    return web.Response(text=html, content_type='text/text', charset='utf-8')


async def download(request):
    args = dict(request.query)
    url = parse.unquote(args['url'])
    type = args.get('type', 'backend')
    if type != 'backend':
        html = await request_api(config.GET_HTML.format(url=url))
        if html:
            return web.Response(text=html, content_type='text/text', charset='utf-8')
    try:
        proxy = args.get('proxy', None)
        if proxy == 'none':
            proxy = None
        else:
            proxy = random.choice(PROXY_POOL)
        async with ClientSession() as session:
            async with session.get(url=url, proxy=proxy,
                                   headers=config.HEADERS,
                                   timeout=config.TIMEOUT) as response:
                bytes = await response.read()
                html = bytes.decode('utf-8')
    except UnicodeDecodeError:
        try:
            html = bytes.decode('gbk')
        except UnicodeDecodeError:
            html = bytes.decode(re.search(r'<meta.+?charset=[^\w]?([-\w]+)', str(bytes)).groups()[0], errors='ignore')
    except:
        html = ''
    finally:
        html = re.sub(r'\s+', ' ', html).replace('&amp;', '&')
        print(datetime.now(), url, len(html))
    return web.Response(text=html, content_type='text/text', charset='utf-8')


async def proxies():
    while True:
        try:
            global PROXY_POOL
            PROXY_POOL = json.loads(await request_api(config.GET_PROXY))
        except:
            pass
        finally:
            await asyncio.sleep(config.API_FREQUENCY)


async def request_api(url):
    try:
        async with ClientSession() as session:
            async with session.get(url=url, timeout=config.TIMEOUT) as resp:
                html = await resp.text()
            return html
    except:
        return ''


def loop_server():
    loop = asyncio.new_event_loop()
    future = init(loop)
    loop.run_until_complete(future)
    loop.run_forever()


def loop_proxies():
    loop = asyncio.new_event_loop()
    future = proxies()
    loop.run_until_complete(future)
    loop.run_forever()


if __name__ == '__main__':
    Thread(target=loop_proxies).start()
    Thread(target=loop_server).start()
