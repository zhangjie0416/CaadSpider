import re
import time
from pymysql import escape_string


def text_handler(text, functions):
    # 统一调用，封装了所有的处理函数
    text = re.sub(r'<.*?>', '', text)
    for _function in functions:
        try:
            function_name = re.match(r'\w+', _function)[0]
            text = getattr(ExtendedFunctions, function_name)(text, _function)
            if not text:
                text = ''
                break
        except:
            text = ''
    return escape_string(text)


class ExtendedFunctions:
    # 提取数据的方法
    @staticmethod
    def replace(text, _function):
        args = re.search(r'"(.*?)","(.*)"', _function)
        text = re.sub(args[1], args[2], text)
        return text

    @staticmethod
    def match(text, _function):
        args = re.search(r'"(.*?)","(.*)"', _function)
        text = re.search(args[1], text)[args[2] and int(args[2]) or 0]
        return text

    @staticmethod
    def incise(text, _function):
        args = re.search(r'"(.*?)","(.*)"', _function)
        text = re.split(args[1] == ' ' and '\s+' or args[1], text)[int(args[2]) - 1]
        return text

    @staticmethod
    def filter(text, _function):
        args = re.search(r'"(.*?)","(.*)"', _function)
        if (re.search(args[1], text) and args[2].lower() == 'yes') or (
                not re.search(args[1], text) and args[2].lower() == 'no'):
            text = text
        else:
            text = ''
        return text

    @staticmethod
    def formatime(text, _function=''):
        types = {"秒": 1, "分钟": 60, "小时": 60 * 60, "天": 60 * 60 * 24, "周": 60 * 60 * 24 * 7, "月": 60 * 60 * 24 * 30,
                 "年": 60 * 60 * 24 * 365}
        args = re.search(r'(\d+)([^前]+)前?', text)
        if len(args.groups()) == 2 and args[2] in list(types.keys()):
            seconds = time.time() - types[args[2]] * int(args[1])
            text = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(seconds))
        else:
            text = text
        return text
