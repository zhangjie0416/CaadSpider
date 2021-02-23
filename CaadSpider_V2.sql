/*
 Navicat Premium Data Transfer

 Source Server         : 172.16.3.133
 Source Server Type    : MySQL
 Source Server Version : 50721
 Source Host           : 172.16.3.133:3306
 Source Schema         : CaadSpider_V2

 Target Server Type    : MySQL
 Target Server Version : 50721
 File Encoding         : 65001

 Date: 19/10/2018 17:38:59
*/

-- ----------------------------
-- Table structure for spider_setting
-- ----------------------------
DROP TABLE IF EXISTS `spider_setting`;
CREATE TABLE `spider_setting`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'id',
  `create_time` datetime(0) NOT NULL COMMENT '创建时间',
  `update_time` datetime(0) NOT NULL DEFAULT '1970-01-01 08:00:00' COMMENT '更新时间',
  `group_name` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '分组名称',
  `task_name` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '任务名称',
  `is_example` int(11) NOT NULL DEFAULT 0 COMMENT '是否模板',
  `is_full` int(11) NOT NULL DEFAULT 0 COMMENT '是否全量',
  `first_urls` json COMMENT '一级网址',
  `urls_xpath` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '' COMMENT '网址xpath',
  `data_xpath` json COMMENT '数据xpath',
  `first_url` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '' COMMENT '测试一级网址',
  `second_url` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '' COMMENT '测试二级网址',
  `timer` int(11) NOT NULL DEFAULT 0 COMMENT '定时采集',
  `urls_status` int(11) NOT NULL DEFAULT 0 COMMENT 'urls状态',
  `data_status` int(11) NOT NULL DEFAULT 0 COMMENT 'data状态',
  `begin_time` datetime(0) NOT NULL DEFAULT '1970-01-01 08:00:00' COMMENT '开始时间',
  `finish_time` datetime(0) NOT NULL DEFAULT '1970-01-01 08:00:00' COMMENT '结束时间',
  `progress` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '0%=0/0(0)' COMMENT '采集进度',
  `user_id` bigint(20) NOT NULL COMMENT '用户id',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix-create_time`(`create_time`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2132 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for spider_user
-- ----------------------------
DROP TABLE IF EXISTS `spider_user`;
CREATE TABLE `spider_user`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `create_time` datetime(0) NOT NULL,
  `update_time` datetime(0) NOT NULL DEFAULT '1900-01-01 00:00:00',
  `username` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `password` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `company` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `is_read` int(20) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 28 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for spider_version
-- ----------------------------
DROP TABLE IF EXISTS `spider_version`;
CREATE TABLE `spider_version`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `create_time` date DEFAULT NULL,
  `version` varchar(8) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `description` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 29 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;
