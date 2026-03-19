# -*- coding: utf-8 -*-
import pymysql, re, sys

conn = pymysql.connect(
    host='127.0.0.1', port=3306, user='root', password='123456',
    database='audit_platform', charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)
cur = conn.cursor()
cur.execute('SELECT rid, rname, pattern, language FROM auditrule WHERE enabled=1')
rules = cur.fetchall()
conn.close()

print('=== 数据库中的规则 ===')
for r in rules:
    print(f"rid={r['rid']}  lang={r['language']}  pattern={repr(r['pattern'])}")

print()
print('=== 测试匹配 ===')
test_lines = [
    ("sql = \"SELECT * FROM user WHERE name = '%s'\" % username", 'python sql注入(%拼接)'),
    ("cur.execute(sql)",                                          'python execute调用'),
    ("os.system(cmd)",                                           'python 命令注入'),
    ("DB_PASSWORD = 'Admin@2026'",                               'python 硬编码密码'),
    ("password = '123456'",                                      'python password='),
    ('ResultSet rs = stmt.executeQuery("SELECT * FROM user WHERE id = " + userId)', 'java sql注入'),
    ("ObjectInputStream ois = new ObjectInputStream(bis)",       'java 反序列化'),
    ("eval($user_input)",                                        'php eval'),
    ("include($page)",                                           'php 文件包含'),
    ("document.getElementById('output').innerHTML = comment",   'js xss innerHTML'),
    ("base.__proto__.isAdmin = true",                            'js 原型链污染'),
    ("full = base + '../etc/passwd'",                            '路径穿越 ../'),
]

for line, desc in test_lines:
    matched = []
    for r in rules:
        try:
            if re.search(r['pattern'], line, re.IGNORECASE):
                matched.append(f"rid={r['rid']}({r['rname']})")
        except re.error as e:
            matched.append(f"rid={r['rid']} 正则ERROR:{e}")
    status = '命中: ' + ', '.join(matched) if matched else '【未命中】'
    print(f"{status}")
    print(f"  描述: {desc}")
    print(f"  代码: {line[:90]}")
    print()

