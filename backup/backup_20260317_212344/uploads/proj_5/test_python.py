# -*- coding: utf-8 -*-
"""
Python 测试样本 - 包含多种安全漏洞（仅用于审计工具测试）
"""
import os
import pymysql

# ===== 1. SQL 注入（规则1：execute\s*\(.*%） =====
# 规则要求同一行有 execute( 且有 %，写在一行触发
def get_user(username):
    conn = pymysql.connect(host='localhost', user='root', password='123456', db='test')
    cur = conn.cursor()
    cur.execute("SELECT * FROM user WHERE name='%s'" % username)   # 漏洞：字符串%拼接传入execute
    return cur.fetchone()

# ===== 2. 命令注入（规则2：os\.system） =====
def run_ping(host):
    os.system("ping -c 4 " + host)   # 漏洞：用户输入直接传入shell

# ===== 3. 敏感信息硬编码（规则6：password\s*=） =====
password = "Admin@2026"          # 漏洞：密码硬编码
db_password = "Mysql@Root123"   # 漏洞：密码硬编码

# ===== 4. 路径穿越（规则7：\.\.\/） =====
def read_file(filename):
    # 漏洞：用户输入中含 ../ 可穿越目录
    full = "/var/www/uploads/../../../etc/" + filename
    with open(full, 'r') as f:
        return f.read()

# ===== 正常代码（不应触发） =====
def safe_query(username):
    conn = pymysql.connect(host='localhost', user='root', password='123456', db='test')
    cur = conn.cursor()
    cur.execute("SELECT * FROM user WHERE name = %s", (username,))  # 参数化查询
    return cur.fetchone()

