# -*- coding: utf-8 -*-
import os, sys, re
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())

import pymysql
conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='123456',
                       database='audit_platform', charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)
cur = conn.cursor()
cur.execute('SELECT * FROM auditrule WHERE enabled=1 AND (language=%s OR language=%s)', ('java','all'))
rules = cur.fetchall()
conn.close()

filepath = os.path.abspath('uploads/proj_5/TestVulns.java')
print(f'文件: {filepath}')
print(f'文件存在: {os.path.isfile(filepath)}')
print(f'适用规则数: {len(rules)}')
print()

with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

print(f'文件共 {len(lines)} 行')
print()

for rule in rules:
    print(f"规则 rid={rule['rid']} {rule['rname']} pattern={repr(rule['pattern'])}")
    matched_lines = []
    try:
        pat = re.compile(rule['pattern'], re.IGNORECASE)
        for i, line in enumerate(lines, 1):
            if pat.search(line):
                matched_lines.append(f"  第{i}行: {line.rstrip()[:80]}")
    except re.error as e:
        print(f"  !! 正则编译错误: {e}")
    if matched_lines:
        print(f"  命中 {len(matched_lines)} 处:")
        for m in matched_lines:
            print(m)
    else:
        print(f"  未命中")
    print()

