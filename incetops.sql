/*
Navicat MySQL Data Transfer

Date: 2018-08-08 14:57:13
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for incetops_db
-- ----------------------------
DROP TABLE IF EXISTS `incetops_db`;
CREATE TABLE `incetops_db` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT 'id',
  `sd` varchar(140) NOT NULL COMMENT '短描述',
  `host` varchar(100) NOT NULL COMMENT 'db地址',
  `port` int(5) unsigned NOT NULL DEFAULT '3306' COMMENT 'db端口',
  `user` varchar(32) NOT NULL DEFAULT 'user' COMMENT 'db用户',
  `passwd` varchar(255) NOT NULL DEFAULT '' COMMENT 'db密码',
  `ris` varchar(30) DEFAULT '' COMMENT '推荐使用的Inception服务地址，格式是db:port',
  `ctime` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '创建时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for incetops_inception
-- ----------------------------
DROP TABLE IF EXISTS `incetops_inception`;
CREATE TABLE `incetops_inception` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT 'id',
  `sd` varchar(140) NOT NULL COMMENT '短描述',
  `host` varchar(100) NOT NULL COMMENT 'Inception地址',
  `port` int(5) unsigned NOT NULL DEFAULT '6669' COMMENT 'Inception端口',
  `ctime` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_hostport` (`host`,`port`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for incetops_task
-- ----------------------------
DROP TABLE IF EXISTS `incetops_task`;
CREATE TABLE `incetops_task` (
  `taskId` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT '任务ID',
  `dbId` int(10) unsigned NOT NULL COMMENT 'incetops_db id',
  `sd` varchar(64) NOT NULL COMMENT '任务描述',
  `inception` varchar(30) NOT NULL COMMENT '使用的Inception服务地址，格式是db:port',
  `applicant` varchar(100) NOT NULL COMMENT '申请人姓名',
  `ctime` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '申请时间',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT '任务状态,0-执行成功 3-执行中 4-执行异常 5-已取消 6-已驳回 7-定时任务等待执行',
  `statusMsg` varchar(5000) DEFAULT '' COMMENT '状态解释信息',
  `timer` int(11) NOT NULL DEFAULT '0' COMMENT '多少秒后定时执行,0-立即执行,大于0时需要将status设为7,等待执行',
  `timer_id` varchar(36) NOT NULL DEFAULT '' COMMENT '定时执行时job.id,用以取消任务',
  `sqlContent` text NOT NULL COMMENT '通过inception执行的sql语句',
  `autoviewResult` longtext NOT NULL COMMENT '自动审核结果,json',
  `autoviewSQLSHA1` varchar(500) DEFAULT '' COMMENT '任务中每条大SQL语句对应的唯一HASH值，多个使用逗号隔开，此值根据autoviewCheck生成，以便查询osc',
  `enableIgnoreWarnings` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否忽略警告，0-不忽略 1-忽略',
  `enableRemoteBackup` tinyint(1) NOT NULL DEFAULT '1' COMMENT '是否启用远程备份，0-不备份 1-备份',
  `executeResult` longtext COMMENT '执行结果,json',
  `ftime` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '执行任务的时间',
  PRIMARY KEY (`taskId`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT='通过inception执行sql任务的记录表';
