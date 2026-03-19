# -*- coding: utf-8 -*-
# Python 漏洞样本2

import os
import pymysql
import subprocess

# 硬编码密码（规则6）
password = "SuperAdmin@2026"
db_password = "Mysql#Root!123"
api_password = "ApiKey_hardcoded"

# SQL注入：execute + % 同一行（规则1）
def login(username, pwd):
    conn = pymysql.connect(host='127.0.0.1', user='root', password='123456', db='app')
    cur = conn.cursor()
    cur.execute("SELECT * FROM user WHERE name='%s' AND pwd='%s'" % (username, pwd))
    return cur.fetchone()

def search_product(keyword):
    conn = pymysql.connect(host='127.0.0.1', user='root', password='123456', db='shop')
    cur = conn.cursor()
    cur.execute("SELECT * FROM product WHERE name LIKE '%%%s%%'" % keyword)
    return cur.fetchall()

def get_order(order_id):
    conn = pymysql.connect(host='127.0.0.1', user='root', password='123456', db='shop')
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders WHERE id=%s" % order_id)
    return cur.fetchone()

# 命令注入：os.system（规则2）
def compress_file(filename):
    os.system("zip -r output.zip " + filename)

def run_script(script_name):
    os.system("bash /opt/scripts/" + script_name)

def check_host(ip):
    os.system("ping -c 1 " + ip)

# 路径穿越（规则7）
def read_log(logname):
    with open("/var/log/app/../../../etc/" + logname) as f:
        return f.read()

def download_file(path):
    with open("/data/uploads/../../../" + path, 'rb') as f:
        return f.read()

