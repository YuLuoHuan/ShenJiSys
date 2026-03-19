# -*- coding: utf-8 -*-
# Python 漏洞样本3

import os
import pymysql

# 硬编码密码（规则6）
password = "Payment@Secret2026"
db_password = "Redis_Pass#999"
smtp_password = "SmtpAuth@2026"

# SQL注入（规则1）
def get_user_by_email(email):
    conn = pymysql.connect(host='127.0.0.1', user='root', password='123456', db='crm')
    cur = conn.cursor()
    cur.execute("SELECT * FROM user WHERE email='%s'" % email)
    return cur.fetchone()

def delete_record(table, rid):
    conn = pymysql.connect(host='127.0.0.1', user='root', password='123456', db='crm')
    cur = conn.cursor()
    cur.execute("DELETE FROM %s WHERE id=%s" % (table, rid))
    conn.commit()

def update_balance(uid, amount):
    conn = pymysql.connect(host='127.0.0.1', user='root', password='123456', db='pay')
    cur = conn.cursor()
    cur.execute("UPDATE account SET balance=%s WHERE uid='%s'" % (amount, uid))
    conn.commit()

# 命令注入（规则2）
def convert_image(filename):
    os.system("convert " + filename + " output.png")

def send_mail(addr):
    os.system("sendmail " + addr + " < /tmp/mail.txt")

def backup_db(dbname):
    os.system("mysqldump " + dbname + " > /tmp/backup.sql")

# 路径穿越（规则7）
def get_template(name):
    with open("/app/templates/../../../" + name) as f:
        return f.read()

def export_file(filename):
    with open("/var/export/../../../tmp/" + filename, 'rb') as f:
        return f.read()

