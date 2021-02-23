DROP TABLE IF EXISTS `spider_user`;
CREATE TABLE IF NOT EXISTS `spider_user` (
  `id`          BIGINT      NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `create_time` DATETIME    NOT NULL,
  `update_time` DATETIME    NOT NULL DEFAULT '1900-01-01 00:00:00',
  `username`    VARCHAR(50) NOT NULL,
  `password`    VARCHAR(50) NOT NULL,
  `company`     VARCHAR(50) NOT NULL
);

DROP TABLE IF EXISTS `spider_setting`;
CREATE TABLE IF NOT EXISTS `spider_setting` (
  `id`                    BIGINT        NOT NULL  AUTO_INCREMENT PRIMARY KEY,
  `create_time`           DATETIME      NOT NULL,
  `update_time`           DATETIME      NOT NULL  DEFAULT '1900-01-01 00:00:00',
  `group_name`            VARCHAR(50)   NOT NULL,
  `task_name`             VARCHAR(50)   NOT NULL,
  `first_urls`            VARCHAR(1000) NOT NULL  DEFAULT '',
  `urls_xpath`      VARCHAR(200)  NOT NULL  DEFAULT '',
  `data_xpath` JSON          NULL,
  `is_example`            INT           NOT NULL  DEFAULT 0,
  `data_status`                INT           NOT NULL  DEFAULT 0,
  `timer`                 INT           NOT NULL  DEFAULT 0,
  `finish_time`           DATETIME      NOT NULL  DEFAULT '1900-01-01 00:00:00',
  `progress`              VARCHAR(50)   NOT NULL  DEFAULT '0/0',
  `user_id`               BIGINT        NOT NULL,
  `urls_status`          INT           NOT NULL  DEFAULT 0,
  `is_full`                  INT           NOT NULL  DEFAULT 0
);

DROP TABLE IF EXISTS `spider_data`;
CREATE TABLE IF NOT EXISTS `spider_data` (
  `id`          BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `create_time` DATETIME     NOT NULL,
  `update_time` DATETIME     NOT NULL DEFAULT '1900-01-01 00:00:00',
  `first_url`   VARCHAR(500) NOT NULL DEFAULT '',
  `second_url`  VARCHAR(500) NOT NULL DEFAULT '',
  `data_status`      INT          NOT NULL DEFAULT 0,
  `retry`       INT          NOT NULL DEFAULT 0,
  `data`        JSON         NULL,
  `is_cleaned`  INT          NOT NULL DEFAULT 0,
  INDEX IX_spider_data_update_time_status (update_time DESC, data_status),
  INDEX IX_spider_data_second_url (second_url)
);

DROP TABLE IF EXISTS `spider_version`;
CREATE TABLE IF NOT EXISTS `spider_version` (
  `id`          INT NOT NULL AUTO_INCREMENT,
  `create_time` DATE         DEFAULT NULL,
  `version`     VARCHAR(8)   DEFAULT NULL,
  `description` VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
);

DROP TABLE IF EXISTS `clean_setting`;
CREATE TABLE IF NOT EXISTS `clean_setting` (
  `id`          BIGINT      NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `create_time` DATETIME    NOT NULL,
  `update_time` DATETIME    NOT NULL DEFAULT '1900-01-01 00:00:00',
  `data_status`      INT         NOT NULL DEFAULT 0,
  `finish_time` DATETIME    NOT NULL DEFAULT '1900-01-01 00:00:00',
  `progress`    VARCHAR(50) NOT NULL DEFAULT '0/0',
  `user_id`     BIGINT      NOT NULL,
  `spider_id`   BIGINT      NOT NULL,
  `clean_rules` JSON        NULL
);

DROP TABLE IF EXISTS `clean_data`;
CREATE TABLE IF NOT EXISTS `clean_data` (
  `id`          BIGINT   NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `create_time` DATETIME NOT NULL,
  `clean_old`   JSON     NULL,
  `clean_new`   JSON     NULL,
  `data_id`     BIGINT   NOT NULL,
  INDEX IX_clean_data_create_time (create_time),
  INDEX IX_clean_data_data_id (data_id)
);

