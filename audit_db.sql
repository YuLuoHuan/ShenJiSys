DROP DATABASE IF EXISTS audit_platform;
CREATE DATABASE IF NOT EXISTS audit_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE audit_platform;

CREATE TABLE userinfo (
  uid INT NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  uname VARCHAR(50) NOT NULL COMMENT '用户名',
  passwd VARCHAR(50) NOT NULL COMMENT '登录密码明文',
  realname VARCHAR(50) NOT NULL COMMENT '真实姓名',
  email VARCHAR(100) NOT NULL COMMENT '邮箱地址',
  rolecode TINYINT NOT NULL DEFAULT 2 COMMENT '角色1管理员2审计员',
  status TINYINT NOT NULL DEFAULT 1 COMMENT '状态1启用0禁用',
  createtime DATETIME NOT NULL COMMENT '创建时间',
  PRIMARY KEY (uid),
  UNIQUE KEY uk_uname (uname)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户信息表';

CREATE TABLE secquestion (
  sqid INT NOT NULL AUTO_INCREMENT COMMENT '安全问题ID',
  uid INT NOT NULL COMMENT '关联用户ID',
  question VARCHAR(200) NOT NULL COMMENT '安全问题内容',
  answer VARCHAR(100) NOT NULL COMMENT '答案明文',
  PRIMARY KEY (sqid),
  UNIQUE KEY uk_uid (uid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='密码找回安全问题表';

CREATE TABLE project (
  pid INT NOT NULL AUTO_INCREMENT COMMENT '项目ID',
  pname VARCHAR(100) NOT NULL COMMENT '项目名称',
  pdesc VARCHAR(500) DEFAULT NULL COMMENT '项目描述',
  language VARCHAR(30) NOT NULL COMMENT '目标语言',
  sourcepath VARCHAR(500) NOT NULL COMMENT '源码路径',
  ownerid INT NOT NULL COMMENT '创建人ID',
  status TINYINT NOT NULL DEFAULT 0 COMMENT '0待扫1扫描中2完成3暂停',
  createtime DATETIME NOT NULL COMMENT '创建时间',
  updatetime DATETIME DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (pid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='审计项目表';

CREATE TABLE auditrule (
  rid INT NOT NULL AUTO_INCREMENT COMMENT '规则ID',
  rname VARCHAR(100) NOT NULL COMMENT '规则名称',
  category VARCHAR(50) NOT NULL COMMENT '漏洞类别',
  language VARCHAR(30) NOT NULL COMMENT '适用语言',
  pattern TEXT NOT NULL COMMENT '正则表达式',
  severity TINYINT NOT NULL DEFAULT 2 COMMENT '等级1低2中3高4危急',
  suggestion TEXT DEFAULT NULL COMMENT '修复建议',
  enabled TINYINT NOT NULL DEFAULT 1 COMMENT '1启用0禁用',
  PRIMARY KEY (rid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='代码审计规则表';

CREATE TABLE scantask (
  tid INT NOT NULL AUTO_INCREMENT COMMENT '任务ID',
  pid INT NOT NULL COMMENT '关联项目ID',
  operuid INT NOT NULL COMMENT '操作人ID',
  status TINYINT NOT NULL DEFAULT 0 COMMENT '0等待1进行2完成3暂停4失败',
  progress TINYINT NOT NULL DEFAULT 0 COMMENT '进度0到100',
  totalfiles INT NOT NULL DEFAULT 0 COMMENT '总文件数',
  scannedfiles INT NOT NULL DEFAULT 0 COMMENT '已扫文件数',
  starttime DATETIME DEFAULT NULL COMMENT '开始时间',
  endtime DATETIME DEFAULT NULL COMMENT '结束时间',
  PRIMARY KEY (tid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='扫描任务表';

CREATE TABLE vulninfo (
  vid INT NOT NULL AUTO_INCREMENT COMMENT '漏洞ID',
  tid INT NOT NULL COMMENT '关联任务ID',
  pid INT NOT NULL COMMENT '关联项目ID',
  rid INT NOT NULL COMMENT '命中规则ID',
  filepath VARCHAR(500) NOT NULL COMMENT '文件路径',
  lineno INT NOT NULL COMMENT '行号',
  codesnip TEXT NOT NULL COMMENT '代码片段',
  severity TINYINT NOT NULL COMMENT '等级1低2中3高4危急',
  vulnstate TINYINT NOT NULL DEFAULT 0 COMMENT '0未处理1确认2误报3修复',
  remark VARCHAR(500) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (vid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='漏洞信息表';

CREATE TABLE auditreport (
  repid INT NOT NULL AUTO_INCREMENT COMMENT '报告ID',
  tid INT NOT NULL COMMENT '关联任务ID',
  pid INT NOT NULL COMMENT '关联项目ID',
  operuid INT NOT NULL COMMENT '生成人ID',
  repname VARCHAR(200) NOT NULL COMMENT '报告名称',
  summary TEXT DEFAULT NULL COMMENT '报告摘要',
  pdfpath VARCHAR(500) DEFAULT NULL COMMENT 'PDF路径',
  createtime DATETIME NOT NULL COMMENT '生成时间',
  PRIMARY KEY (repid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='审计报告表';

CREATE TABLE sysconfig (
  cfgid INT NOT NULL AUTO_INCREMENT COMMENT '配置ID',
  cfgkey VARCHAR(100) NOT NULL COMMENT '配置键',
  cfgvalue TEXT NOT NULL COMMENT '配置值',
  cfgdesc VARCHAR(200) DEFAULT NULL COMMENT '配置说明',
  PRIMARY KEY (cfgid),
  UNIQUE KEY uk_cfgkey (cfgkey)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统配置表';

INSERT INTO userinfo VALUES
(1,'admin','123456','系统管理员','admin@auditpro.com',1,1,'2026-01-01 09:00:00'),
(2,'auditor1','123456','张伟','zhangwei@auditpro.com',2,1,'2026-01-05 10:00:00'),
(3,'auditor2','123456','李娜','lina@auditpro.com',2,1,'2026-01-08 10:00:00'),
(4,'auditor3','123456','王强','wangqiang@auditpro.com',2,1,'2026-02-01 09:00:00'),
(5,'manager1','123456','赵敏','zhaoming@auditpro.com',1,1,'2026-02-10 09:00:00');

INSERT INTO secquestion VALUES
(1,1,'您母亲的姓名是什么','王秀英'),
(2,2,'您就读的第一所小学名称','朝阳小学'),
(3,3,'您最喜欢的城市','北京'),
(4,4,'您的出生地','上海'),
(5,5,'您童年宠物的名字','小白');

INSERT INTO project VALUES
(1,'电商平台后端审计','Django电商后端SQL注入XSS检测','python','uploads/proj_1',1,2,'2026-01-10 09:00:00','2026-01-20 17:00:00'),
(2,'OA系统代码审计','企业OA系统Java代码安全审计','java','uploads/proj_2',2,2,'2026-01-15 10:00:00','2026-02-01 16:00:00'),
(3,'PHP论坛安全检测','discuz论坛代码审计','php','uploads/proj_3',3,2,'2026-02-05 09:00:00','2026-02-18 15:00:00'),
(4,'Node.js API审计','前后端分离API安全检测','js','uploads/proj_4',2,3,'2026-03-01 09:00:00','2026-03-05 11:00:00'),
(5,'医疗系统渗透前置审计','医院HIS系统代码安全审计','java','uploads/proj_5',4,0,'2026-03-10 09:00:00',NULL);

INSERT INTO auditrule VALUES
(1,'Python SQL注入检测','sqli','python','execute\\s*\\(.*%',3,'使用参数化查询',1),
(2,'Python命令注入检测','rce','python','os\\.system',4,'禁止用户输入传入shell',1),
(3,'XSS跨站脚本检测','xss','all','innerHTML\\s*=',3,'输出内容做HTML转义',1),
(4,'Java SQL注入检测','sqli','java','executeQuery.*\\+',3,'使用PreparedStatement',1),
(5,'PHP代码执行检测','rce','php','eval\\s*\\(',4,'禁止eval执行用户输入',1),
(6,'敏感信息硬编码','sensitive','all','password\\s*=',2,'使用环境变量存储密码',1),
(7,'路径穿越检测','path','all','\\.\\.\\/|\\.\\.\\\\',3,'路径规范化白名单限制',1),
(8,'PHP文件包含检测','path','php','include\\s*\\(',4,'禁止用户输入用于include',1),
(9,'JS原型链污染检测','other','js','__proto__',2,'避免直接操作原型链',1),
(10,'Java反序列化检测','other','java','ObjectInputStream',3,'反序列化数据严格校验',1);

INSERT INTO scantask VALUES
(1,1,2,2,100,86,86,'2026-01-15 10:00:00','2026-01-15 10:23:00'),
(2,2,2,2,100,143,143,'2026-02-01 09:00:00','2026-02-01 09:41:00'),
(3,3,3,2,100,67,67,'2026-02-18 14:00:00','2026-02-18 14:15:00'),
(4,4,2,3,45,120,54,'2026-03-05 10:00:00',NULL),
(5,1,4,2,100,86,86,'2026-03-08 09:00:00','2026-03-08 09:20:00');

INSERT INTO vulninfo VALUES
(1,1,1,1,'uploads/proj_1/models/user.py',42,'cursor.execute sql inject',3,1,'高危SQL注入待修复'),
(2,1,1,2,'uploads/proj_1/utils/shell.py',18,'os.system call',4,0,NULL),
(3,1,1,6,'uploads/proj_1/config/settings.py',5,'DB_PASSWORD hardcoded',2,3,'已修复'),
(4,2,2,4,'uploads/proj_2/dao/UserDao.java',76,'executeQuery concat',3,1,NULL),
(5,2,2,10,'uploads/proj_2/util/DataUtil.java',23,'ObjectInputStream usage',3,0,NULL),
(6,3,3,5,'uploads/proj_3/forum/user.php',156,'eval POST input',4,1,'严重代码执行风险'),
(7,3,3,8,'uploads/proj_3/forum/template.php',89,'include variable path',4,2,'误报路径已过滤'),
(8,3,3,6,'uploads/proj_3/config/db.php',3,'password hardcoded',2,3,'已修复'),
(9,5,1,1,'uploads/proj_1/views/order.py',91,'executequery concat',3,0,NULL),
(10,5,1,3,'uploads/proj_1/templates/result.html',34,'innerHTML assignment',3,0,NULL);

INSERT INTO auditreport VALUES
(1,1,1,2,'电商平台后端审计报告-2026Q1','发现3处漏洞危急命令注入高危SQL注入中危信息泄露','reports/report_1.pdf','2026-01-15 11:00:00'),
(2,2,2,2,'OA系统代码审计报告-2026Q1','发现2处高危漏洞SQL注入和Java反序列化','reports/report_2.pdf','2026-02-01 10:30:00'),
(3,3,3,3,'PHP论坛安全检测报告-2026Q1','发现3处漏洞危急代码执行误报文件包含中危硬编码密码','reports/report_3.pdf','2026-02-18 15:30:00'),
(4,5,1,4,'电商平台二次审计报告-2026Q1','复查发现2处新漏洞SQL注入与XSS建议全面整改','reports/report_5.pdf','2026-03-08 10:00:00');

INSERT INTO sysconfig VALUES
(1,'scan_timeout','3600','单次扫描最大超时秒数'),
(2,'scan_max_filesize','10485760','单文件最大扫描字节数'),
(3,'scan_file_exts','py,java,php,js,ts,jsx','允许扫描的文件后缀'),
(4,'email_host','smtp.auditpro.com','邮件服务器地址'),
(5,'email_port','465','邮件服务器端口'),
(6,'email_user','notice@auditpro.com','邮件发送账号'),
(7,'email_passwd','EmailPass2026','邮件发送密码'),
(8,'email_enabled','1','是否启用邮件通知'),
(9,'backup_path','backup/','系统备份路径'),
(10,'backup_keep_days','30','备份保留天数'),
(11,'system_name','轻量型代码审计安全检测平台','系统名称'),
(12,'system_version','1.0.0','系统版本号');
