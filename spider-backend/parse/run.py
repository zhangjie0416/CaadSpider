from parsel.selector import Selector
import asyncio
from aiohttp import web, ClientSession
import config
import json
from extend import text_handler
from urllib import parse
import socket
from datetime import datetime
import time


async def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '', index)
    app.router.add_route('GET', '/parser', parser)
    app.router.add_route('POST', '/parser', parser, expect_handler=web.Request.json)
    server = await loop.create_server(app.make_handler(), '0.0.0.0', config.PORT)
    print('Server started at http://{}:{}'.format('127.0.0.1', config.PORT))
    return server


async def index(request):
    html = json.dumps({'service': 'parse', 'name': socket.gethostname(), 'addr': socket.gethostbyname(socket.gethostname())}) + '\n'
    return web.Response(text=html, content_type='text/text', charset='utf-8')


async def parser(request):
    args = request.method == 'GET' and dict(request.query) or dict(await request.json())
    url = args['url']
    xpath = args['xpath']
    type = args.get('type', 'backend')
    proxy = args.get('proxy', None)
    api = '{}?url={}&type={}{}'.format(config.DOWNLOAD_API, url, type, '&proxy={}'.format(proxy) or '')
    async with ClientSession() as session:
        async with session.get(url=api) as response:
            bytes = await response.read()
            html = bytes.decode('utf-8')
    if html:
        time_begin = time.time()
        xhtml = Selector(text=html)
        result = xpath.startswith('{') and get_fields(xhtml, xpath) or get_urls(xhtml, xpath, parse.unquote(url))
        time_pass = str(round(time.time() - time_begin, 3))
    else:
        result = ''
        time_pass = '0'
    log = '{} {}s {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), time_pass.rjust(6, '0'), parse.unquote(url))
    print(log, result)
    return web.Response(text=json.dumps(result, ensure_ascii=False), content_type='text/text', charset='utf-8')


def get_urls(xhtml, xpath, referer):
    urls = []
    _xpaths = xpath.split('|')
    try:
        if _xpaths[0].startswith('/'):  # xpath
            _xpath = '/@href' in _xpaths[0] and _xpaths[0] or '{}//a/@href'.format(_xpaths[0])
            _urls = xpath_extract(xhtml=xhtml, xpath=_xpath, mode='all')
        else:  # regex
            _regex = _xpaths[0]
            _urls = regex_extract(xhtml=xhtml, regex=_regex, mode='all')
        for url in _urls:
            url = parse.urljoin(referer, url)
            if len(_xpaths) > 1: url = text_handler(url, _xpaths[1:])
            if url.startswith('http'): urls.append(url)
        urls = list(set(urls))
    except Exception as e:
        print(e)
        urls = []
    return urls


def get_fields(xhtml, xpath):
    fields_xpath = json.loads(xpath)
    one_fields = {}
    # 固定采集
    for fix_field in fields_xpath['fix_fields']:
        one_fields[fix_field['field']] = fix_field['xpath']
    # 单条采集
    is_valid_one_fields = False  # 采集数据是否有效
    for one_field in fields_xpath['one_fields']:
        _xpaths = one_field['xpath'].split('|')
        if _xpaths[0].startswith('/'):  # xpath
            content = xpath_extract(xhtml=xhtml, xpath=_xpaths[0], mode='one')
        else:  # regex
            content = regex_extract(xhtml=xhtml, regex=_xpaths[0], mode='one')
        content = text_handler(content, _xpaths[1:])
        is_valid_one_fields = content and True or is_valid_one_fields
        one_fields[one_field['field']] = content
        # 多条采集
    all_fields = []
    if fields_xpath['all_xpath']:
        sections = xpath_extract(xhtml=xhtml, xpath=fields_xpath['all_xpath'], mode='all')
        for section in sections:
            is_valid_all_fields = False
            section = Selector(text=section)
            fields = {}
            for all_field in fields_xpath['all_fields']:
                _xpaths = all_field['xpath'].split('|')
                if _xpaths[0].startswith('/'):  # xpath
                    content = xpath_extract(xhtml=section, xpath=_xpaths[0], mode='one')
                else:  # regex
                    content = regex_extract(xhtml=section, regex=_xpaths[0], mode='one')
                content = text_handler(content, _xpaths[1:])
                is_valid_all_fields = content and True or is_valid_all_fields
                fields[all_field['field']] = content
            if is_valid_one_fields or is_valid_all_fields:
                fields = dict(fields, **one_fields)
                all_fields.append(fields)
        return all_fields
    else:
        one_fields = is_valid_one_fields and [one_fields] or []
        return one_fields


def regex_extract(xhtml, regex, mode='all'):
    if mode == 'one':
        return xhtml.re_first(regex) or ''
    else:
        return xhtml.re(regex) or []


def xpath_extract(xhtml, xpath, mode='all'):
    if mode == 'one':
        if '/@' in xpath:
            return xhtml.xpath(xpath).extract_first() or ''
        else:
            return xhtml.xpath(xpath).xpath('string()').extract_first() or ''
    else:
        return xhtml.xpath(xpath).extract() or []


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    future = init(loop)
    loop.run_until_complete(future)
    loop.run_forever()
