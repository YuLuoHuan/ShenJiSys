# 轻量型代码审计安全检测平台

## 项目简介

本项目是一款**轻量型代码审计安全检测平台**，面向中小型团队设计，支持对 Python、Java、PHP、JavaScript 四种主流语言的源码进行自动化安全漏洞扫描。平台采用前后端分离架构，基于正则表达式规则引擎逐行匹配代码中的安全缺陷，并提供可视化漏洞报告与 PDF 导出功能。

---

## 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 后端框架 | Flask | 3.0.3 |
| 数据库驱动 | PyMySQL | 1.1.1 |
| PDF 报告 | ReportLab | 4.2.2 |
| 前端框架 | Vue 3 | 3.4 |
| 前端路由 | Vue Router | 4.3 |
| 状态管理 | Pinia | 2.1 |
| HTTP 客户端 | Axios | 1.6 |
| 数据可视化 | ECharts | 5.5 |
| 构建工具 | Vite | 5.2 |
| 数据库 | MySQL | 5.7+ / 8.0 |

---

## 目录结构

```
code/
├── app.py                  # Flask 入口，注册蓝图，固定工作目录
├── requirements.txt        # Python 依赖
├── audit_db.sql            # 数据库初始化 SQL
├── backend/
│   ├── db.py               # 数据库连接与公共查询函数
│   ├── engine/
│   │   └── scanner.py      # 扫描引擎：文件遍历 + 正则匹配
│   └── routes/
│       ├── auth.py         # 登录/登出/用户认证
│       ├── user.py         # 用户管理（管理员）
│       ├── project.py      # 项目管理
│       ├── scan.py         # 扫描任务：上传、触发、进度查询
│       ├── vuln.py         # 漏洞列表、状态更新
│       ├── report.py       # 报告生成与 PDF 导出
│       ├── rule.py         # 审计规则 CRUD
│       └── dashboard.py    # 统计数据（首页图表）
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   ├── admin/      # 管理员视图（用户管理、规则配置）
│   │   │   └── auditor/    # 审计员视图（项目、扫描、漏洞、报告）
│   │   ├── router/         # 前端路由
│   │   └── stores/         # Pinia 状态仓库
│   ├── package.json
│   └── vite.config.js
├── uploads/                # 项目源码上传存储目录
│   ├── proj_1/             # Python 项目
│   ├── proj_2/             # Java 项目
│   ├── proj_3/             # PHP 项目
│   └── proj_4/             # JavaScript 项目
├── reports/                # 生成的 PDF 报告
└── test_samples/           # 漏洞测试样本文件
```

---

## 数据库配置

数据库信息如下，首次使用需导入初始化 SQL：

```
host:     127.0.0.1
port:     3306
user:     root
password: 123456
database: audit_platform
```

**初始化步骤：**

```bash
mysql -uroot -p123456 < audit_db.sql
```

或在 Navicat 中执行"运行SQL文件" → 选择 `audit_db.sql`。

初始化后将创建以下数据表：

| 表名 | 说明 |
|------|------|
| `userinfo` | 用户信息（管理员/审计员） |
| `project` | 项目信息 |
| `scantask` | 扫描任务记录 |
| `vulninfo` | 漏洞信息 |
| `auditrule` | 审计规则（正则表达式） |
| `reportinfo` | 报告记录 |

---

## 快速启动

### 后端

```bash
cd code
pip install -r requirements.txt
python app.py
```

后端默认监听 `http://127.0.0.1:5000`

### 前端

```bash
cd code/frontend
npm install
npm run dev
```

前端开发服务器默认运行在 `http://localhost:5173`

---

## 功能模块

| 模块 | 说明 |
|------|------|
| 用户管理 | 支持管理员/审计员两种角色，管理员可增删改用户 |
| 项目管理 | 创建项目，指定语言和源码路径 |
| 源码上传 | 支持 `.zip`、`.tar.gz`、`.rar` 压缩包及单个源码文件直接上传 |
| 扫描引擎 | 后台异步线程扫描，实时更新进度（已扫/总文件数）|
| 漏洞管理 | 查看漏洞详情、代码片段、行号，支持标记处理状态 |
| 报告生成 | 一键生成 PDF 扫描报告，含漏洞统计与详情 |
| 审计规则 | 内置10条规则，支持管理员在线增删改、启用/禁用 |
| 统计看板 | 首页展示漏洞分布、项目扫描状态等 ECharts 图表 |

---

## 支持的漏洞类型

| 规则编号 | 漏洞类型 | 支持语言 |
|----------|---------|---------|
| 1 | SQL 注入 | Python |
| 2 | 命令注入 | Python |
| 3 | XSS 跨站脚本 | JavaScript |
| 4 | SQL 注入 | Java |
| 5 | 代码执行（eval） | PHP |
| 6 | 硬编码密码 | 全语言 |
| 7 | 路径穿越 | 全语言 |
| 8 | 文件包含 | PHP |
| 9 | 原型链污染 | JavaScript |
| 10 | 反序列化漏洞 | Java |

---

## 测试样本

`test_samples/` 目录下提供各语言漏洞测试文件，可直接上传到对应项目进行扫描验证：

| 文件 | 语言 | 覆盖漏洞 |
|------|------|---------|
| `test_python.py` | Python | SQL注入、命令注入、硬编码密码、路径穿越 |
| `vuln_python2.py` | Python | SQL注入×3、命令注入×3、硬编码×3、路径穿越×2 |
| `vuln_python3.py` | Python | SQL注入×3、命令注入×3、硬编码×3、路径穿越×2 |
| `TestVulns.java` | Java | SQL注入、反序列化、硬编码密码、路径穿越 |
| `VulnService.java` | Java | SQL注入×3、反序列化×2、硬编码×3、路径穿越×2 |
| `VulnDao.java` | Java | SQL注入×4、反序列化×2、硬编码×2、路径穿越×1 |
| `test_vulns.php` | PHP | 代码执行、文件包含、硬编码密码、路径穿越 |
| `vuln_php2.php` | PHP | 代码执行×4、文件包含×4、硬编码×3、路径穿越×3 |
| `vuln_php3.php` | PHP | 代码执行×3、文件包含×3、硬编码×3、路径穿越×4 |
| `test_vulns.js` | JavaScript | XSS、原型链污染、硬编码密码、路径穿越 |
| `vuln_js2.js` | JavaScript | XSS×5、原型链污染×3、硬编码×3、路径穿越×3 |
| `vuln_js3.js` | JavaScript | XSS×5、原型链污染×4、硬编码×3、路径穿越×3 |

---

## 默认账号

| 角色 | 用户名 | 密码 |
|------|-------|------|
| 管理员 | admin | 123456 |
| 审计员 | auditor | 123456 |

