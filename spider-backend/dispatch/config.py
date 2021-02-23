# api
SQL_API = "http://172.16.2.82:10010"
STORE_API = "http://172.16.2.82:10014"
# ==========================================Sql API=======================================================================
SpiderSetting_select_setting = SQL_API + '/spider_setting/select_setting?setting_id={}'
SpiderSetting_select_spiders = SQL_API + '/spider_setting/select_spiders?type={}'
SpiderSetting_update_progress = SQL_API + '/spider_setting/update_progress?setting_id={}'
SpiderSetting_update_setting = SQL_API + '/spider_setting/update_setting'
SpiderSetting_update_statistic = SQL_API + '/spider_setting/update_statistic'
SpiderUrls_select_urls = SQL_API + '/spider_urls/select_urls'
SpiderData_select_urls = SQL_API + '/spider_data/select_urls?setting_id={}&limit={}'
SpiderData_delete_data = SQL_API + '/spider_data/delete_data'
# ===========================================Store API=========================================================================
Store_spider_urls = STORE_API + '/crawl_urls'
Store_spider_data = STORE_API + '/crawl_data'
# ==========================================Redis API==========================================================================
DELETE_KEYS = SQL_API + '/spider_logs/delete_keys?setting_id={setting_id}'

DATA_CONCURRENCE = 10  # 采集字段每10秒单个任务并发数量
URLS_CONCURRENCE = 10  # 采集网址每10秒单个任务并发数量

PORT = 10015
