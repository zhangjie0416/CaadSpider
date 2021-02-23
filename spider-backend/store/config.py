# api
# ============================================解析===========================================================
SQL_API = "http://172.16.2.82:10010"
PARSE_API = "http://172.16.2.82:10013/parser"
# ============================================SQL API========================================================
INSERT_URLS = SQL_API + '/spider_urls/insert_urls'  # 二级url入库
INSERT_DATA = SQL_API + '/spider_data/insert_data'  # 数据入库
DELETE_URLS = SQL_API + '/spider_urls/delete_urls'  # 二级url入库

SELECT_RETRY = SQL_API + '/spider_logs/select_retry?key={key}'
INSERT_RETRY = SQL_API + '/spider_logs/insert_retry?key={key}&value={value}'
REMOVE_RETRY_ONE = SQL_API + '/spider_logs/remove_retry_one?key={key}&value={value}'
REMOVE_RETRY_MAX = SQL_API + '/spider_logs/remove_retry_max?key={key}&value={value}'

PORT = 10014
