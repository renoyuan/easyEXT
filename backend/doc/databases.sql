CREATE DATABASE `idp` /*!40100 DEFAULT CHARACTER SET utf8 */;

CREATE TABLE `ele_value` (
  `page` int(11) NOT NULL COMMENT '页码',
  `pos` varchar(999) NOT NULL COMMENT '坐标',
  `value` varchar(999) DEFAULT NULL COMMENT '要素值',
  `task_id` int(11) NOT NULL,
  `file_id` int(11) NOT NULL,
  `element_id` int(11) NOT NULL,
  `ele_value_id` int(11) DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_time` datetime NOT NULL COMMENT '创建时间',
  `updated_time` datetime NOT NULL COMMENT '更新时间',
  `is_del` tinyint(4) DEFAULT NULL COMMENT '0存在 1删除',
  PRIMARY KEY (`id`),
  KEY `task_id` (`task_id`),
  KEY `file_id` (`file_id`),
  KEY `element_id` (`element_id`),
  KEY `ele_value_id` (`ele_value_id`),
  CONSTRAINT `ele_value_ibfk_1` FOREIGN KEY (`task_id`) REFERENCES `task` (`id`),
  CONSTRAINT `ele_value_ibfk_2` FOREIGN KEY (`file_id`) REFERENCES `file` (`id`),
  CONSTRAINT `ele_value_ibfk_3` FOREIGN KEY (`element_id`) REFERENCES `element` (`id`),
  CONSTRAINT `ele_value_ibfk_4` FOREIGN KEY (`ele_value_id`) REFERENCES `ele_value` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `element` (
  `name` varchar(999) NOT NULL COMMENT '对外输出要素标识',
  `model_name` varchar(999) DEFAULT NULL COMMENT '模型中标识',
  `name_cn` varchar(999) NOT NULL COMMENT '要素标识中文',
  `is_group` int(11) NOT NULL COMMENT '是否编组',
  `t_type` int(11) NOT NULL COMMENT '0 单值 1 多值 2 组标识',
  `status` int(11) NOT NULL COMMENT '任务状态',
  `scene_id` int(11) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_time` datetime NOT NULL COMMENT '创建时间',
  `updated_time` datetime NOT NULL COMMENT '更新时间',
  `is_del` tinyint(4) DEFAULT NULL COMMENT '0存在 1删除',
  PRIMARY KEY (`id`),
  KEY `scene_id` (`scene_id`),
  CONSTRAINT `element_ibfk_1` FOREIGN KEY (`scene_id`) REFERENCES `scene` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `file` (
  `t_type` int(11) NOT NULL COMMENT '文件类型 0上传文件 1拆页后图片 2ocr返回图片 3ocr_json 4format_ocr_json5format_table_ocr_json 6ext_json 6format_ext_json 7印章识别结果',
  `page_no` int(11) NOT NULL COMMENT '页码',
  `file_url` varchar(999) NOT NULL COMMENT 'fastdfs_url',
  `file_name` varchar(999) NOT NULL COMMENT '文件名',
  `format` int(11) NOT NULL COMMENT '文件格式 0jpg 1jpeg 2png 3tif 4pdf 5doc',
  `task_id` int(11) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_time` datetime NOT NULL COMMENT '创建时间',
  `updated_time` datetime NOT NULL COMMENT '更新时间',
  `is_del` tinyint(4) DEFAULT NULL COMMENT '0存在 1删除',
  PRIMARY KEY (`id`),
  KEY `task_id` (`task_id`),
  CONSTRAINT `file_ibfk_1` FOREIGN KEY (`task_id`) REFERENCES `task` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `model_info` (
  `model_id` varchar(999) NOT NULL COMMENT '模型标识',
  `model_name` varchar(999) DEFAULT NULL COMMENT '模型名称',
  `ip` varchar(999) NOT NULL COMMENT 'ip',
  `port` varchar(999) NOT NULL COMMENT 'port',
  `api_path` varchar(999) NOT NULL COMMENT 'api_path',
  `default_para` varchar(999) DEFAULT NULL COMMENT '场景名',
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_time` datetime NOT NULL COMMENT '创建时间',
  `updated_time` datetime NOT NULL COMMENT '更新时间',
  `is_del` tinyint(4) DEFAULT NULL COMMENT '0存在 1删除',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `msg_task` (
  `msg_info` varchar(999) NOT NULL COMMENT '任务信息',
  `status` int(11) NOT NULL COMMENT '任务状态',
  `task_id` int(11) NOT NULL,
  `file_id` int(11) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_time` datetime NOT NULL COMMENT '创建时间',
  `updated_time` datetime NOT NULL COMMENT '更新时间',
  `is_del` tinyint(4) DEFAULT NULL COMMENT '0存在 1删除',
  PRIMARY KEY (`id`),
  KEY `task_id` (`task_id`),
  KEY `file_id` (`file_id`),
  CONSTRAINT `msg_task_ibfk_1` FOREIGN KEY (`task_id`) REFERENCES `task` (`id`),
  CONSTRAINT `msg_task_ibfk_2` FOREIGN KEY (`file_id`) REFERENCES `file` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `post_process` (
  `path` varchar(999) NOT NULL COMMENT '后处理路径',
  `element_id` int(11) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_time` datetime NOT NULL COMMENT '创建时间',
  `updated_time` datetime NOT NULL COMMENT '更新时间',
  `is_del` tinyint(4) DEFAULT NULL COMMENT '0存在 1删除',
  PRIMARY KEY (`id`),
  KEY `element_id` (`element_id`),
  CONSTRAINT `post_process_ibfk_1` FOREIGN KEY (`element_id`) REFERENCES `element` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `scene` (
  `scene_id` varchar(999) DEFAULT NULL COMMENT '对外提供场景标识',
  `model_id` varchar(999) DEFAULT NULL COMMENT '模型标识',
  `scene` varchar(999) DEFAULT NULL COMMENT '场景名',
  `scene_cn` varchar(999) DEFAULT NULL COMMENT '场景名中文',
  `scene_model` varchar(999) DEFAULT NULL COMMENT '调用模型场景名',
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_time` datetime NOT NULL COMMENT '创建时间',
  `updated_time` datetime NOT NULL COMMENT '更新时间',
  `is_del` tinyint(4) DEFAULT NULL COMMENT '0存在 1删除',
  PRIMARY KEY (`id`),
  UNIQUE KEY `scene_id` (`scene_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `scene_model_association` (
  `scene_id` int(11) DEFAULT NULL,
  `model_info_id` int(11) DEFAULT NULL,
  KEY `scene_id` (`scene_id`),
  KEY `model_info_id` (`model_info_id`),
  CONSTRAINT `scene_model_association_ibfk_1` FOREIGN KEY (`scene_id`) REFERENCES `scene` (`id`),
  CONSTRAINT `scene_model_association_ibfk_2` FOREIGN KEY (`model_info_id`) REFERENCES `model_info` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `task` (
  `parent_id` int(11) DEFAULT NULL COMMENT '父级任务标识',
  `satus` int(11) NOT NULL COMMENT '任务状态 0 待执行 1执行中 2完成 3失败 ',
  `t_type` int(11) NOT NULL COMMENT '任务类型 0要素抽取 1印章识别 2表格识别 3印章识别',
  `sub_type` int(11) NOT NULL COMMENT '二级任务类型 0调用ocr 1调用nlp/llm 2format',
  `file_count` int(11) NOT NULL COMMENT '文件数量',
  `ori_file_count` int(11) NOT NULL COMMENT '原始文件数量',
  `scene_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_time` datetime NOT NULL COMMENT '创建时间',
  `updated_time` datetime NOT NULL COMMENT '更新时间',
  `is_del` tinyint(4) DEFAULT NULL COMMENT '0存在 1删除',
  PRIMARY KEY (`id`),
  KEY `parent_id` (`parent_id`),
  KEY `scene_id` (`scene_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `task_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `task` (`id`),
  CONSTRAINT `task_ibfk_2` FOREIGN KEY (`scene_id`) REFERENCES `scene` (`id`),
  CONSTRAINT `task_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `user` (
  `name` varchar(999) NOT NULL COMMENT '姓名',
  `phone` varchar(999) DEFAULT NULL COMMENT '手机号',
  `account` varchar(999) DEFAULT NULL COMMENT '账号',
  `password` varchar(999) DEFAULT NULL COMMENT '密码MD5加密',
  `enable_password` varchar(999) DEFAULT NULL COMMENT '明文密码',
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_time` datetime NOT NULL COMMENT '创建时间',
  `updated_time` datetime NOT NULL COMMENT '更新时间',
  `is_del` tinyint(4) DEFAULT NULL COMMENT '0存在 1删除',
  PRIMARY KEY (`id`),
  UNIQUE KEY `account` (`account`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `user_scene_association` (
  `user_id` int(11) DEFAULT NULL,
  `scene_id` int(11) DEFAULT NULL,
  KEY `user_id` (`user_id`),
  KEY `scene_id` (`scene_id`),
  CONSTRAINT `user_scene_association_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`),
  CONSTRAINT `user_scene_association_ibfk_2` FOREIGN KEY (`scene_id`) REFERENCES `scene` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;